import json
import logging

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)


@login_required
def chat_view(request):
    if request.user.role not in ('employee', 'mentor','admin'):
        raise PermissionDenied
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []
    history = request.session['chat_history']
    return render(request, 'assistant/chat.html', {'history': history})


@require_POST
@login_required
def ask_view(request):
    if request.user.role not in ('employee', 'mentor', 'admin'):
        return JsonResponse({'error': 'forbidden'}, status=403)
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
    except Exception:
        return JsonResponse({'error': 'invalid request'}, status=400)
    if not question:
        return JsonResponse({'error': 'empty question'}, status=400)

    history = request.session.get('chat_history', [])
    answer, sources, context = _rag_query(question, history)

    history.append({'role': 'user', 'text': question, 'context': context})
    history.append({'role': 'wade', 'text': answer, 'sources': sources})
    request.session['chat_history'] = history[-40:]
    request.session.modified = True

    return JsonResponse({'answer': answer, 'sources': sources})


@login_required
def clear_history_view(request):
    if request.method == 'POST':
        request.session['chat_history'] = []
        request.session.modified = True
    return redirect('assistant:chat')


def _rag_query(question, history=None):
    """Perform RAG: embed question → search Chroma → call Ollama."""
    try:
        import chromadb
        from admin_panel.models import SystemSettings
        from knowledge.embeddings import embed_query
        from knowledge.signals import _get_collection

        ollama_model = SystemSettings.get('ollama_model', 'llama3')
        llm_backend = SystemSettings.get('llm_backend', 'ollama')
        llm_url = settings.LM_STUDIO_URL if llm_backend == 'lmstudio' else settings.OLLAMA_URL

        # Embed the question with multilingual-e5-large
        query_embedding = embed_query(question)

        # Query Chroma
        chroma = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        collection = _get_collection(chroma)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            include=['documents', 'metadatas'],
        )

        docs = results['documents'][0] if results['documents'] else []
        metas = results['metadatas'][0] if results['metadatas'] else []
        context = '\n\n'.join(docs) if docs else 'Информация не найдена.'

        # Deduplicate sources
        seen = set()
        sources = []
        for m in metas:
            if m.get('article_slug') and m['article_slug'] not in seen:
                seen.add(m['article_slug'])
                sources.append({'title': m.get('article_title', ''), 'slug': m['article_slug']})

        # Call Ollama chat
        system_prompt = (
            'Ты — Вэйд (W.A.D.E.), помощник по адаптации сотрудников в Targem Games. '
            'Ты человекоподобный робот — харизматичный, с юмором и лёгкой дерзостью, но всегда полезный. '
            'Отвечай только на основе предоставленного контекста из базы знаний. Если вопрос личный и относится к тебе как к персонажу, то можешь отвечать от себя.'
            'Всегда обращай внимание на историю диалога.'
            'Если нужной информации в контексте нет — честно скажи об этом. '
            'Отвечай на русском языке.'
        )
        messages = [{'role': 'system', 'content': system_prompt}]
        for entry in (history or [])[-10:]:
            role = 'assistant' if entry['role'] == 'wade' else 'user'
            if role == 'user' and entry.get('context'):
                content = f'Контекст:\n{entry["context"]}\n\nВопрос: {entry["text"]}'
            else:
                content = entry['text']
            messages.append({'role': role, 'content': content})
        messages.append({'role': 'user', 'content': f'Контекст:\n{context}\n\nВопрос: {question}'})
        gen_resp = requests.post(
            f'{llm_url}/v1/chat/completions',
            json={
                'model': ollama_model,
                'messages': messages,
                'stream': False,
            },
            timeout=600,
        )
        gen_resp.raise_for_status()
        answer = gen_resp.json()['choices'][0]['message']['content']
        return answer, sources, context

    except Exception as e:
        logger.warning('RAG query failed: %s', e)
        return (
            f'Хм, что-то пошло не так. Похоже система временно недоступна. '
            f'Попробуй позже! (Детали: {type(e).__name__})',
            [],
            '',
        )
