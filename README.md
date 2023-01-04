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
>> results
>> {'word': '<profanity-word>', 'index': 4, 'start': 15, 'end': 31}

text = st.censor_profanity(text='Some text with <profanity-word>.')
>> text
>> "Some text with ***."
```