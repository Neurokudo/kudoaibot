# app/services/gpt_templates.py
"""GPT инструкции и шаблоны из babka-bot-clean"""

import json
import logging
from typing import Optional

log = logging.getLogger(__name__)

# Стили из babka-bot-clean
STYLE_HINTS = {
    "Анимэ": {
        "subject": "anime-style characters with cel-shaded outlines, exaggerated expressions, large eyes, simplified textures. Each object drawn in anime style with sharp outlines and flat shading.",
        "scene": "background like hand-painted anime background art with watercolor gradients, flat colors with subtle gradients, pastel palette with saturated highlights.",
        "lighting": "light bloom effects, stylized lighting without realistic shadows, clean highlights.",
        "mood": "Energetic, expressive, colorful.",
        "shot": "Cinematic anime shot, medium-wide, dolly-in, dynamic angles typical of anime films. Add falling petals, glowing city lights, stylized clouds."
    },
    "LEGO": {
        "subject": "EVERYTHING MUST BE MADE OF LEGO BRICKS: grandmother as LEGO minifigure with yellow skin, cylindrical hands, LEGO hair piece, brick-patterned clothing. All objects are LEGO blocks with visible studs and plastic texture.",
        "scene": "Complete LEGO world: ground made of LEGO baseplates, all buildings and objects constructed from LEGO bricks with visible studs and seams. No realistic textures allowed.",
        "lighting": "Bright studio lighting with strong plastic reflections, pure saturated colors typical of LEGO sets, no realistic shadows.",
        "mood": "Playful, toy-like, artificial.",
        "shot": "Low angle as if filming miniatures, smooth camera movements, shallow depth of field to emphasize toy scale."
    },
}

def style_instructions(style_name: Optional[str]) -> str:
    """Получить инструкции стиля для GPT"""
    if not style_name or style_name not in STYLE_HINTS:
        return ""
    s = STYLE_HINTS[style_name]
    # Компактная директива стиля на английском для Veo
    return (
        f"{s['subject']} "
        f"{s['scene']} "
        f"Lighting: {s['lighting']}. "
        f"Mood: {s['mood']}. "
        f"Shot: {s['shot']}."
    )

def improve_scene(user_text: str, mode: str = "normal") -> str:
    """Улучшение сцены через GPT (из babka-bot-clean)"""
    from app.services.ai_helper import get_openai_client
    
    style = {
        "normal": "Сделай рабочую сцену.",
        "complex": "Добавь деталей, сделай сцену насыщеннее и визуально сложнее.",
        "simple": "Упрости сцену, оставь только главное.",
        "absurd": "Сделай сцену более абсурдной и смешной."
    }.get(mode, "Сделай рабочую сцену.")
    
    sys = (
        "Ты редактор коротких видеосцен. Формулируй именно ОДНУ СЦЕНУ: кто где что делает. "
        "Длительность ~8 секунд, ОДНА сцена без разделения на части. Без поэзии/оценок. "
        "Субтитры и текст в кадре запрещены. Не используй кавычки и тире. "
        "НЕ создавай несколько сцен или сцен 1/2. Только ОДНА цельная сцена. "
        f"{style} Напиши 1–2 коротких предложения, описывающих ОДНУ сцену."
    )
    
    temp = {"normal": 0.65, "complex": 0.85, "simple": 0.55, "absurd": 0.9}[mode]
    
    try:
        client = get_openai_client()
        if not client:
            return user_text
            
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sys},
                {"role": "user", "content": user_text}
            ],
            temperature=temp,
            max_tokens=140,
        )
        
        result = response.choices[0].message.content.strip()
        return result if result else user_text
        
    except Exception as e:
        log.error(f"GPT improve_scene error: {e}")
        return user_text

def improve_scene_with_phrase(scene_text: str, phrase: str, mode: str = "complex") -> str:
    """Улучшает сцену, сохраняя фразу (из babka-bot-clean)"""
    from app.services.ai_helper import get_openai_client
    
    if not phrase:
        return improve_scene(scene_text, mode)
    
    # Извлекаем фразу из сцены, если она там есть
    import re
    quote_pattern = r'"[^"]*"'
    scene_without_phrase = re.sub(quote_pattern, '', scene_text).strip()
    
    # Улучшаем сцену без фразы
    improved_scene = improve_scene(scene_without_phrase, mode)
    
    # Встраиваем фразу обратно
    embed_prompt = (
        f"Встрой фразу в улучшенное описание сцены как речь персонажа.\n\n"
        f"Улучшенная сцена: {improved_scene}\n"
        f"Фраза: {phrase}\n\n"
        f"ТРЕБОВАНИЯ:\n"
        f"- Встрой фразу как прямую речь персонажа в кавычках\n"
        f"- Добавь слова автора типа 'говорит', 'восклицает', 'шепчет' и т.д.\n"
        f"- Фраза должна звучать естественно в контексте сцены\n"
        f"- Сцена должна остаться целостной и логичной\n"
        f"- НЕ добавляй никаких технических деталей, стилей, ориентаций\n"
        f"- НЕ добавляй строки типа 'Style:', 'Replica:', 'Orientation:'\n\n"
        f"Верни ТОЛЬКО обновленное описание сцены без дополнительных комментариев."
    )
    
    try:
        client = get_openai_client()
        if not client:
            return improved_scene
            
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": embed_prompt}],
            max_tokens=200,
            temperature=0.7,
        )
        result = resp.choices[0].message.content.strip() if resp else ""
        
        # Очищаем результат от лишних строк
        lines = result.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Пропускаем строки с техническими деталями
            if (line.startswith('- Style:') or 
                line.startswith('- Replica:') or 
                line.startswith('- Orientation:') or
                line.startswith('Style:') or
                line.startswith('Replica:') or
                line.startswith('Orientation:')):
                continue
            cleaned_lines.append(line)
        
        return ' '.join(cleaned_lines) if cleaned_lines else improved_scene
        
    except Exception as e:
        log.error(f"GPT embed phrase error: {e}")
        return improved_scene

def create_rich_json_template(scene: str, style: Optional[str], replica: Optional[str],
                             mode: Optional[str], aspect_ratio: str, context: Optional[str]) -> str:
    """
    Создает промт-директиву для GPT, чтобы он вернул ГОТОВЫЙ JSON под Veo.
    Скопировано из babka-bot-clean
    """
    from app.services.ai_helper import get_openai_client
    
    style_text = style_instructions(style)

    rep_rules = ""
    if mode == "reportage":
        rep_rules = (
            "Reporter must be Russian-speaking female, speak Russian. "
            "No English lines. Scene 1: reporter speaks to camera; grandmother with object/animal behind. "
            "Scene 2: CLOSE on the SAME grandmother in the SAME yard/clothes/object — strict visual continuity; "
            "repeat characters/props/background from scene 1."
        )

    base_rules = (
        "Return VALID JSON only (no comments). "
        "Prohibit any on-screen text/subtitles/logos/watermarks. "
        "Duration strictly 8 seconds. "
        "IMPORTANT: If the scene involves a grandmother (бабушка/бабка), the voice must be described as 'old female voice, 65-80 years old, warm and experienced tone' in the voiceover section."
    )
    
    # Специальные правила для режима NEUROKUDO
    nkudo_rules = ""
    if mode == "neurokudo":
        nkudo_rules = (
            "NEUROKUDO STYLE RULES - Use these EXACT examples:\n"
            "LOCATIONS: 'Zalupinsk backyard', 'Soviet kitchen with green wallpaper', 'chicken coop interior', 'muddy yard with puddles'\n"
            "GRANDMOTHER: 'elderly (~75-85 y.o.)', 'blue floral housecoat', 'red headscarf tied under chin', 'rubber boots', 'quilted jacket'\n"
            "CREATURES: SIMPLE and REALISTIC actions only - animals can walk, run, swim, eat, sleep, stand, sit\n"
            "NO CLOTHING on animals - they are naked/natural\n"
            "NO COMPLEX ACTIONS - no acrobatics, dancing, rolling, complex movements\n"
            "GOOD examples: 'whales swimming in pool', 'elephants eating grass', 'crocodiles sleeping', 'penguins standing'\n"
            "BAD examples: 'penguins in boots', 'crocodiles doing acrobatics', 'elephants wearing clothes'\n"
            "DIALOGUE TONE: 'calm, matter-of-fact', 'proud explanation', 'as if normal', 'village accent'\n"
            "VISUAL DETAILS: 'rusty metal frame', 'wooden fence', 'enamel kettle', 'wicker basket', 'straw on floor', 'muddy ground'\n"
            "CAMERA: 'handheld documentary', 'shaky realism', 'close-up on grandmother's face', 'wide shot showing scale'\n"
            "EXAMPLES:\n"
            "- 'elderly Russian grandmother (~78 y.o.) stands proudly in rubber boots, holding metal bucket, gesturing toward whales swimming'\n"
            "- 'grandmother in blue housecoat feeds velociraptors in chicken coop like regular chickens'\n"
            "- 'babushka in quilted jacket calmly explains about dinosaurs standing in her backyard'\n"
        )

    sys = (
        "You are a prompt engineer for Google Veo 3.0.\n"
        f"{base_rules} {rep_rules} {nkudo_rules}\n"
        "CRITICAL: Apply visual styling STRICTLY to ALL visual elements. "
        "Insert style_directives content into these fields: "
        "subject.description, scene.location, lighting, mood and shot (camera).\n"
        "The style MUST be visible in the final video - this is the most important requirement!\n"
        "Apply the style consistently across all visual elements.\n"
        "Use this schema (keys in English; values can be Russian):\n"
        "{\n"
        '  "model": "veo-3.0-fast",\n'
        '  "duration": 8,\n'
        '  "aspect_ratio": "9:16|16:9",\n'
        '  "style_directives": "конкретные указания по виду героя/одежды/материалов/окружения/палитры/света/камеры/поста",\n'
        '  "shot": {"composition": "...", "camera_motion": "...", "lens": "35mm", "frame_rate": "24fps", "film_grain": "subtle"},\n'
        '  "subject": {"description": "... (со стилем)", "voice_sync": false},\n'
        '  "scene": {"location": "... (со стилем)", "time_of_day": "..."},\n'
        '  "action": "what happens in 8s concisely",\n'
        '  "voiceover": {"voice": "...", "line": "..."},\n'
        '  "characters": [{"name":"...", "position":"...", "appearance":"... (со стилем)", "action":"..."}],\n'
        '  "ambient": "fx list",\n'
        '  "lighting": "освещение с учётом стиля",\n'
        '  "mood": "настроение, вытекающее из стиля",\n'
        '  "restrictions": "No text or logos."\n'
        "}\n"
        "Always keep the JSON compact and consistent."
    )

    usr = (
        f"scene_text: {scene}\n"
        f"replica: {replica or ''}\n"
        f"aspect_ratio: {aspect_ratio}\n"
    )
    if style_text:
        usr += f"IMPORTANT: Apply this style to ALL visual elements: {style_text}\n"
        usr += f"Make sure the style is embedded in subject.description, scene.location, lighting, mood, and shot fields.\n"
    if context:
        usr += f"context_for_continuity: {context}\n"

    try:
        client = get_openai_client()
        if not client:
            # fallback JSON если GPT недоступен
            style_stub = style_text or ""
            return json.dumps({
                "model": "veo-3.0-fast",
                "duration": 8,
                "aspect_ratio": aspect_ratio,
                "style_directives": style_stub,
                "shot": {"composition": "medium shot", "camera_motion": "static",
                         "lens": "35mm", "frame_rate": "24fps", "film_grain": "subtle"},
                "subject": {"description": scene, "voice_sync": False},
                "scene": {"location": "generic", "time_of_day": "day"},
                "action": "8s action",
                "voiceover": {"voice": "female", "line": replica or ""},
                "characters": [],
                "ambient": "light fx",
                "lighting": "natural",
                "mood": "neutral",
                "restrictions": "No text or logos"
            }, ensure_ascii=False)
            
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": sys},
                      {"role": "user", "content": usr}],
            temperature=0.55,
            max_tokens=1300,
        )
        return (r.choices[0].message.content or "").strip()
    except Exception as e:
        log.error("GPT JSON convert error: %s", e)
        # fallback максимально честный и простой
        style_stub = style_text or ""
        return json.dumps({
            "model": "veo-3.0-fast",
            "duration": 8,
            "aspect_ratio": aspect_ratio,
            "style_directives": style_stub,
            "shot": {"composition": "medium shot", "camera_motion": "static",
                     "lens": "35mm", "frame_rate": "24fps", "film_grain": "subtle"},
            "subject": {"description": scene, "voice_sync": False},
            "scene": {"location": "generic", "time_of_day": "day"},
            "action": "8s action",
            "voiceover": {"voice": "female", "line": replica or ""},
            "characters": [],
            "ambient": "light fx",
            "lighting": "natural",
            "mood": "neutral",
            "restrictions": "No text or logos"
        }, ensure_ascii=False)

def random_meme_scene() -> str:
    """Генерация случайной мемной сцены (из babka-bot-clean)"""
    import random
    
    subjects = ["Бабка", "Дед", "Тётка с авоськой", "Дворник", "Курьер", "Официант",
                "Школьник с рюкзаком", "Рокер", "Бизнес леди", "Мужик в телогрейке"]
    locations = ["у подъезда", "на рынке", "в метро", "на остановке", "в парке",
                 "во дворе панельного дома", "на набережной", "у киоска с шаурмой"]
    props = ["арбузом", "самоваром", "гигантским пакетом чипсов", "надувным крокодилом",
             "плюшевым медведем", "огромной лампой торшером", "портретом кота", "резиновым утёнком"]
    items_plural = ["апельсинами", "булочками", "плюшевыми утками", "сосисками в тесте",
                    "листовками", "ладошками из поролона", "магнитиками", "стеклянными банками"]
    npcs = ["охранником", "продавщицей семечек", "контролёром", "диспетчером такси", "дворовой кошкой"]
    vehicles = ["скейтборде", "самокате", "тележке из супермаркета", "велике без седла"]
    templates = [
        "{s} едет на {veh} {loc}",
        "{s} спорит с {npc} {loc}",
        "{s} жонглирует {items} {loc}",
        "{s} танцует с {prop} {loc}",
        "{s} раздаёт {items} {loc}",
        "{s} пытается упаковать {prop} в пакет {loc}",
        "{s} толкает тележку с {prop} {loc}",
        "{s} фотографируется с {prop} {loc}",
    ]
    t = random.choice(templates); s = random.choice(subjects); loc = random.choice(locations)
    if "{veh}" in t:  return t.format(s=s, veh=random.choice(vehicles), loc=loc)
    if "{npc}" in t:  return t.format(s=s, npc=random.choice(npcs), loc=loc)
    if "{items}" in t:return t.format(s=s, items=random.choice(items_plural), loc=loc)
    return t.format(s=s, prop=random.choice(props), loc=loc)
