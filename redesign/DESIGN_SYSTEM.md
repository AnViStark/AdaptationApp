# Targem Games — Design System
## Система адаптации новых сотрудников

> Этот документ является источником правды для реализации UI. Используй его вместе с `targem-tokens.css` и `components-reference.html`.

---

## 1. Принципы

- **Один шрифт** — только Barlow Condensed (Google Fonts), все веса от 400 до 900
- **Светлая тема** — белые карточки на сером фоне, никаких тёмных блоков
- **Один акцентный цвет** — циан `#4DD8E8`, используется для интерактивных элементов, border-top акцентов, иконок, активных состояний
- **Иерархия через вес** — заголовки 900, подзаголовки 700–800, body 400–500
- **Border-top** на карточках вместо теней — `4px solid var(--accent)` обозначает важные блоки

---

## 2. Цвета

| Токен | Значение | Применение |
|---|---|---|
| `--accent` | `#4DD8E8` | Кнопки, активные состояния, border-top, иконки, ссылки |
| `--bg` | `#EAEAEA` | Фон страницы |
| `--white` | `#FFFFFF` | Фон карточек, панелей |
| `--ink` | `#1A1A1A` | Основной текст |
| `--muted` | `#777777` | Вторичный текст, подписи |
| `--subtle` | `#F4F4F4` | Фон инпутов, тегов, чипов |
| `--border` | `#E0E0E0` | Рамки карточек, разделители |

### Акцент с прозрачностью (используй через opacity или hex):
- Фон иконок: `#4DD8E812` (~7% opacity)
- Hover-свечение: `#4DD8E833` (~20% opacity)
- Подсветка строки: `#4DD8E815` (~8% opacity)

### Цвета бейджей достижений (фиксированные, не переменные):
| № | Фон | Рамка | Иконка |
|---|---|---|---|
| 1 | `#FFF4CC` | `#F5C800` | `#C89A00` |
| 2 | `#CCF0FF` | `#4DD8E8` | `#4DD8E8` |
| 3 | `#CCFFE8` | `#2ECC71` | `#1A9E55` |
| 4 | `#F0CCFF` | `#9B59FF` | `#7B3FE4` |
| 5 | `#FFEDCC` | `#FF9500` | `#CC6A00` |

---

## 3. Типографика

**Подключение:** `https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;600;700;800;900&display=swap`

```css
font-family: 'Barlow Condensed', sans-serif;
```

| Роль | weight | size | transform | letter-spacing |
|---|---|---|---|---|
| Page title (H1) | 900 | 48px | uppercase | -0.01em |
| Hero title | 900 | 58px | uppercase | -0.01em |
| Card title | 800 | 20–22px | uppercase | 0.04em |
| Section heading | 800 | 16–18px | uppercase | 0.06–0.07em |
| Label / eyebrow | 500–600 | 13px | uppercase | 0.10–0.12em |
| Body text | 400 | 15–17px | none | normal |
| Body small | 400 | 13px | none | normal |
| Badge / tag | 700 | 11–13px | uppercase | 0.06em |
| Stat number | 900 | 32–38px | — | — |
| Stat label | 500 | 13px | uppercase | 0.10em |
| Nav link | 500–700 | 15px | uppercase | 0.05em |
| Button | 700 | 15–16px | uppercase | 0.06–0.07em |

**Правило:** `line-height: 0.95` для крупных заголовков, `1.4–1.6` для body.

---

## 4. Отступы и сетка

| Токен | Значение |
|---|---|
| `--radius` | `18px` (дефолт, меняется через tweak) |
| `--radius-sm` | `calc(var(--radius) * 0.6)` |
| `--radius-xs` | `6–8px` (теги, чипы) |
| `--page-padding` | `36px` |
| `--page-max-width` | `1140px` |
| `--gap` | `16–20px` между карточками |
| `--card-padding` | `24–28px` внутри карточек |

**Сетки:**
- Главная (карточки разделов): `grid-template-columns: repeat(4, 1fr)`
- Тренажёр: `repeat(2, 1fr)`
- База знаний: `repeat(4, 1fr)`
- Профиль: `280px 1fr`
- Маршрут: `1fr 300px`

---

## 5. Компоненты

### 5.1 Навигация (top nav)

- Высота: `58px`
- Фон: `var(--white)`, нижняя граница `1px solid var(--border)`
- `position: sticky; top: 0; z-index: 100`
- Логотип: текст «TARGEM» weight 900 + «GAMES» weight 500 muted
- Ссылки: Barlow Condensed 15px uppercase, `padding: 7px 15px`, `border-radius: var(--radius-sm)`
- **Активная ссылка:** `background: var(--accent); color: white`
- **Неактивная ссылка:** `color: var(--muted)`
- User chip: аватар-инициалы + имя, `background: var(--subtle)`, `border-radius: 40px`
- Кнопка «Выход»: outlined, `border: 1px solid var(--border)`

### 5.2 Карточка (базовая)

```
background: var(--white)
border: 1px solid var(--border)
border-radius: var(--radius)
padding: 24–28px
```

**Акцентная карточка** (важный блок):
```
border-top: 4px solid var(--accent)
```

**Hover:**
```
transform: translateY(-3px)
box-shadow: 0 10px 28px rgba(77,216,232,0.2)
transition: transform 0.15s, box-shadow 0.15s
```

### 5.3 Кнопка (primary)

```css
background: var(--accent);
color: white;
border: none;
border-radius: var(--radius-sm);
padding: 10–11px 22–24px;
font-family: 'Barlow Condensed';
font-weight: 700;
font-size: 15–16px;
text-transform: uppercase;
letter-spacing: 0.06–0.07em;
cursor: pointer;
```

**Outlined кнопка:**
```css
background: transparent;
border: 1px solid var(--border);
color: var(--muted);
```

### 5.4 XP / Progress bar

```html
<div class="xp-bar-track">
  <div class="xp-bar-fill" style="width: 75%"></div>
</div>
```

```css
.xp-bar-track {
  background: #D8D8D8;
  border-radius: var(--radius);
  height: 8px; /* или 12px для большого */
  overflow: hidden;
}
.xp-bar-fill {
  background: var(--accent);
  height: 100%;
  border-radius: var(--radius);
  transition: width 0.6s ease;
}
```

### 5.5 Stat pill (число + подпись)

```html
<div class="stat-pill">
  <span class="stat-value">160</span>
  <span class="stat-label">Баллов</span>
</div>
```

```css
.stat-pill {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: calc(var(--radius) * 0.8);
  padding: 12px 20px;
  text-align: center;
}
.stat-value {
  display: block;
  font-weight: 900;
  font-size: 38px;
  color: var(--accent);
  line-height: 1;
}
.stat-label {
  display: block;
  font-weight: 500;
  font-size: 13px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.10em;
  margin-top: 3px;
}
```

### 5.6 Badge / статус-тег

```html
<span class="badge badge--accent">Готово</span>
<span class="badge badge--muted">Не начато</span>
```

```css
.badge {
  font-weight: 700;
  font-size: 11–13px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 3–4px 8–10px;
  border-radius: 6–7px;
  white-space: nowrap;
}
.badge--accent { background: var(--accent); color: white; }
.badge--accepted { background: rgba(77,216,232,0.12); color: var(--accent); }
.badge--muted { background: var(--subtle); color: var(--muted); }
```

### 5.7 Чекпойнт задания (выполненный)

```html
<div class="task-item task-item--done">
  <div class="task-check">✓</div>
  <span class="task-title">Название задания</span>
  <span class="badge badge--accent">Готово</span>
</div>
```

```css
.task-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border-radius: calc(var(--radius) * 0.8);
}
.task-item--done {
  background: rgba(77,216,232,0.08);
  border: 1.5px solid rgba(77,216,232,0.2);
}
.task-check {
  width: 26px; height: 26px;
  background: var(--accent);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 13px; flex-shrink: 0;
}
.task-title {
  flex: 1;
  text-decoration: line-through;
  color: var(--muted);
  font-size: 16px;
}
```

### 5.8 Чипы подсказок (страница Вэйда)

```html
<button class="suggestion-chip">Как оформить отгул?</button>
```

```css
.suggestion-chip {
  background: var(--subtle);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 7px 14px;
  font-family: 'Barlow Condensed';
  font-weight: 500;
  font-size: 15px;
  color: var(--ink);
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}
.suggestion-chip:hover {
  border-color: var(--accent);
  color: var(--accent);
}
```

### 5.9 Поле ввода

```css
input, textarea {
  font-family: 'Barlow Condensed';
  font-size: 17px;
  color: var(--ink);
  background: var(--white);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  padding: 15–16px 18–22px;
  outline: none;
  transition: border-color 0.2s;
  width: 100%;
}
input:focus, textarea:focus {
  border-color: var(--accent);
}
```

### 5.10 Бейдж достижения

```html
<div class="achievement-badge" style="--badge-bg:#FFF4CC; --badge-border:#F5C800; --badge-icon:#C89A00">
  <div class="achievement-badge__icon"><!-- SVG иконка --></div>
  <span class="achievement-badge__title">Сотня</span>
  <span class="achievement-badge__desc">Набрано 100 баллов</span>
</div>
```

```css
.achievement-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 12px 16px;
  background: var(--badge-bg);
  border: 1.5px solid var(--badge-border);
  border-radius: calc(var(--radius) * 0.8);
  text-align: center;
  gap: 10px;
}
.achievement-badge__icon {
  width: 52px; height: 52px;
  background: white;
  border-radius: 50%;
  border: 2px solid var(--badge-border);
  display: flex; align-items: center; justify-content: center;
}
.achievement-badge__title {
  font-weight: 800;
  font-size: 16px;
  color: var(--ink);
}
.achievement-badge__desc {
  font-weight: 400;
  font-size: 13px;
  color: var(--muted);
}
```

---

## 6. Экраны

### 6.1 Главная (/)
**Layout:** hero-блок (2 колонки: контент + иллюстрация) → 4 карточки разделов
- Hero: левая часть — заголовок + прогресс, правая — место для иллюстрации/персонажа
- 4 карточки: Мой маршрут, База знаний, Помощник Вэйд, Тренажёр
- Каждая карточка: область для изображения сверху → заголовок → описание → ссылка

### 6.2 Мой маршрут (/route или /onboarding)
**Layout:** заголовок + статы → прогресс-бар → `[задания | сайдбар]`
- Сайдбар (300px): этапы маршрута (список с чекбоксами) + блок наставника
- Основная область: табы этапов + список заданий текущего этапа

### 6.3 База знаний (/knowledge)
**Layout:** заголовок → строка поиска → 4 карточки категорий
- Каждая категория: иконка папки + название + кол-во статей + ссылка

### 6.4 Помощник Вэйд (/wade)
**Layout:** шапка с аватаром → область чата → блок подсказок → поле ввода
- Шапка: 2 колонки — описание + иллюстрация аватара
- Подсказки: чипы с частыми вопросами, клик = вставить в поле
- Поле ввода: полная ширина, кнопка отправки справа внутри

### 6.5 Тренажёр (/trainer)
**Layout:** заголовок → 2×2 сетка карточек заданий
- Карточка задания: статус-тег + заголовок + краткое описание + баллы + CTA
- `border-top: 4px solid var(--accent)` у принятых заданий, `var(--border)` у новых

### 6.6 Профиль (/profile)
**Layout:** `[левая колонка 280px | правая колонка]`
- Левая: аватар-инициалы + имя + роль + таблица метаданных + форма смены пароля
- Правая: карточка прогресса маршрута + сетка достижений 3 колонки

---

## 7. Иллюстрации (плейсхолдеры → реальный арт)

Все иллюстративные области сейчас заняты полосатыми плейсхолдерами. При замене на реальный арт сохрани те же размеры и `border-radius`:

| Место | Размер | Описание |
|---|---|---|
| Hero (главная) | ~340×260px | Персонаж / игровой арт Targem |
| Карточка раздела (верх) | ~120×70px | Тематическая иллюстрация раздела |
| Аватар Вэйда | ~140×100px | Персонаж-бот Вэйд |

---

## 8. Правила для реализации на Django templates

1. Подключи `targem-tokens.css` в `base.html` через `{% load static %}`
2. Шрифт Barlow Condensed подключай в `<head>` через Google Fonts
3. Каждый компонент — отдельный `{% include %}` partial в `templates/components/`
4. Активный пункт навигации определяй через `{% if request.resolver_match.url_name == 'home' %}` и добавляй класс `nav-link--active`
5. Прогресс-бар: передавай `pct` как контекст (`{{ progress_pct }}`), ставь как `style="width: {{ progress_pct }}%"`
6. Цвета достижений — цикл по индексу: `{{ forloop.counter0|divisibleby:... }}` или передай цвет в контексте
