<div align="center">
  <p>
    <a align="center" href="" target="_blank">
      <img
        width="1280"
        src="https://github.com/safevideo/safetext/assets/44926076/9af66dde-3a93-4c5b-b802-cb31dffcb2e5"
      >
    </a>
  </p>
</div>

# safetext

Rule-based profanity checking tool for English and Turkish.

### installation

```bash
pip install safetext
```

### usage

```python
from safetext import SafeText

st = SafeText(language='en')

results = st.check_profanity(text='Some text with <profanity-word>.')
results
>> {'word': '<profanity-word>', 'index': 4, 'start': 15, 'end': 31}

text = st.censor_profanity(text='Some text with <profanity-word>.')
text
>> "Some text with ***."
```

### automated language detection

- automatically set language from text:

```python
from safetext import SafeText

eng_text = "This story is about to take a dark turn."

st = SafeText(language=None)
st.set_language_from_text(eng_text)

st.language
>> 'en'
```

- automatically set language from .srt (subtitle) file:

```python
from safetext import SafeText

turkish_srt_file_path = "turkish.srt"

st = SafeText(language=None)
st.set_language_from_srt(turkish_srt_file_path)

st.language
>> 'tr'
```
