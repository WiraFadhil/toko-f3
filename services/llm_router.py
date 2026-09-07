import json
import re
import time

import requests

import config

PROVIDERS = {
    'groq': {
        'base_url': 'https://api.groq.com/openai/v1',
        'model': 'openai/gpt-oss-120b',
        'env_key': 'GROQ_API_KEY',
    },
    'cerebras': {
        'base_url': 'https://api.cerebras.ai/v1',
        'model': 'gpt-oss-120b',
        'env_key': 'CEREBRAS_API_KEY',
    },
    'mistral': {
        'base_url': 'https://api.mistral.ai/v1',
        'model': 'open-mistral-nemo',
        'env_key': 'MISTRAL_API_KEY',
    },
    'gemini': {
        'base_url': 'https://generativelanguage.googleapis.com/v1beta/openai',
        'model': 'gemini-3.6-flash',
        'env_key': 'GEMINI_API_KEY',
    },
}

# preferensi model per provider (dipilih dari daftar /models saat runtime)
MODEL_PREFERENCE = {
    'groq': ['openai/gpt-oss-120b', 'groq/compound', 'qwen/qwen3.8-27b', 'openai/gpt-oss-20b', 'qwen/qwen3.6-27b'],
    'cerebras': ['gpt-oss-120b', 'qwen-3.8-27b', 'gemma-4-31b'],
    'mistral': ['open-mistral-nemo', 'mistral-small-latest', 'mistral-nemo', 'ministral-8b'],
    'gemini': ['gemini-3.6-flash', 'gemini-3.5-flash', 'gemini-3.1-flash-lite', 'gemini-flash-latest', 'gemini-2.5-flash'],
}

COOLDOWN_SECONDS = 15
_cooldowns = {}
_round_robin = {}
_model_cache = {}
_dead_providers = set()


def get_api_key(provider_name):
    provider = PROVIDERS.get(provider_name)
    if not provider:
        return ''
    return getattr(config, provider['env_key'], '')


def _model_candidates(name):
    """Tentukan daftar kandidat model untuk sebuah provider.

    Prioritas: preferensi MODEL_PREFERENCE yang cocok dengan daftar /models
    live dari provider (cache per-proses), fallback ke model bawaan.
    """
    if name in _model_cache:
        return _model_cache[name]

    candidate = [PROVIDERS[name]['model']]
    try:
        resp = requests.get(
            PROVIDERS[name]['base_url'] + '/models',
            headers={'Authorization': 'Bearer ' + get_api_key(name)},
            timeout=15,
        )
        if resp.status_code == 200:
            ids = [(m.get('id') or '') for m in resp.json().get('data', [])]
            ids = [i[7:] if i.startswith('models/') else i for i in ids]
            picked = []
            for pref in MODEL_PREFERENCE.get(name, []):
                for i in ids:
                    if i == pref or i.startswith(pref):
                        picked.append(i)
                        break
            if picked:
                candidate = picked
    except Exception:
        pass

    _model_cache[name] = candidate
    return candidate


def available_providers():
    order = [p.strip().lower() for p in config.AI_PROVIDER_ORDER.split(',') if p.strip()]
    for name in order:
        if name in PROVIDERS and get_api_key(name):
            yield name
    for name in PROVIDERS:
        if name not in order and get_api_key(name):
            yield name


def _is_available(name):
    until = _cooldowns.get(name, 0)
    return time.monotonic() >= until


def _mark_cooldown(name):
    _cooldowns[name] = time.monotonic() + COOLDOWN_SECONDS


def _chat_with(name, messages, max_tokens, temperature, model=None):
    provider = PROVIDERS[name]
    payload = {
        'model': model or provider['model'],
        'messages': messages,
        'max_tokens': max_tokens,
        'temperature': temperature,
    }
    resp = requests.post(
        provider['base_url'] + '/chat/completions',
        headers={
            'Authorization': 'Bearer ' + get_api_key(name),
            'Content-Type': 'application/json',
        },
        json=payload,
        timeout=config.AI_REQUEST_TIMEOUT,
    )
    if resp.status_code != 200:
        raise RuntimeError(f'{name}: HTTP {resp.status_code} {resp.text[:200]}')
    data = resp.json()
    choice = data.get('choices', [{}])[0]
    content = (choice.get('message') or {}).get('content') or ''
    if not content.strip():
        raise RuntimeError(f'{name}: balasan kosong')
    return content


def chat(messages, max_tokens=2048, temperature=0.3):
    """Panggil LLM di beberapa provider gratis secara bergantian.

    Jika provider gagal (rate limit, down, timeout) otomatis lanjut ke
    provider berikutnya. Mengembalikan dict {content, provider, error}.
    """
    errors = []
    candidates = list(available_providers())
    if not candidates:
        return {'content': '', 'provider': None, 'error': 'Tidak ada provider AI yang terkonfigurasi.'}

    # mulai dari provider berbeda tiap request (round-robin) agar kuota seimbang
    _round_robin.setdefault('idx', 0)
    start = _round_robin['idx'] % len(candidates)
    _round_robin['idx'] = start + 1
    order = [candidates[(start + i) % len(candidates)] for i in range(len(candidates))]

    started_at = time.monotonic()
    tried = 0
    for name in order:
        if name in _dead_providers or not _is_available(name):
            continue
        tried += 1
        if tried > config.AI_MAX_PROVIDERS and time.monotonic() - started_at > 6:
            break
        model_error = None
        for model in _model_candidates(name):
            try:
                content = _chat_with(name, messages, max_tokens, temperature, model=model)
                return {'content': content, 'provider': name, 'error': None}
            except Exception as e:
                model_error = e
                # model tidak ditemukan/tidak punya akses -> coba kandidat berikutnya
                if 'model_not_found' not in str(e).lower() and 'does not exist' not in str(e).lower():
                    break
        if model_error:
            _mark_cooldown(name)
            # error auth/payment permanen -> jangan dicoba lagi selama proses berjalan
            if any(f'HTTP {c} ' in str(model_error) for c in (401, 402, 403)):
                _dead_providers.add(name)
            errors.append(f'{name}: {model_error}')

    return {'content': '', 'provider': None, 'error': '; '.join(errors) or 'Tidak ada provider AI yang terkonfigurasi.'}


def parse_reply(text):
    """Parsing JSON balasan model: {"jawaban": "...", "gambar": ["url"]}. Bila gagal, anggap teks biasa."""
    text = (text or '').strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, dict):
                jawaban = str(data.get('jawaban') or data.get('answer') or '').strip()
                gambar = data.get('gambar') or data.get('images') or []
                if not isinstance(gambar, list):
                    gambar = [gambar]
                gambar = [g for g in gambar if isinstance(g, str) and g.startswith('http')]
                return {
                    'jawaban': jawaban or 'Maaf, saya belum bisa menjawab pertanyaan itu.',
                    'gambar': gambar,
                }
        except (json.JSONDecodeError, ValueError):
            pass
    return {'jawaban': text or 'Maaf, saya belum bisa menjawab pertanyaan itu.', 'gambar': []}