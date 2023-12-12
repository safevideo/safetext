<div align="center">
  <p>
    <a align="center" href="" target="_blank">
      <img
        width="1280"
        src="https://github.com/safevideo/safetext/assets/44926076/9af66dde-3a93-4c5b-b802-cb31dffcb2e5"
      >
    </a>
  </p>

[![version](https://badge.fury.io/py/safetext.svg)](https://badge.fury.io/py/safetext)
[![downloads](https://pepy.tech/badge/safetext)](https://pepy.tech/project/safetext)
[![license](https://img.shields.io/pypi/l/safetext)](LICENSE)

</div>

## 🤔 why safetext?

**Detect. Filter. Protect.**

- **Effortless Profanity Management**: Instantly identify and censor profanity with just one line of code.
- **Multilingual Capability**: Fluent in five languages, designed for easy expansion.
- **Optimized for Content Moderation**: Perfect for efficiently moderating and cleaning up text in various applications.
- **Automated**: Smart language detection for quick setup.

## 📦 installation

easily install **safetext** with pip:

```bash
pip install safetext
```

## 🎯 quickstart

### check and censor profanity

```python
>>> from safetext import SafeText

>>> st = SafeText(language='en')

>>> results = st.check_profanity(text='Some text with <profanity-word>.')
>>> results
{'word': '<profanity-word>', 'index': 4, 'start': 15, 'end': 31}

>>> text = st.censor_profanity(text='Some text with <profanity-word>.')
>>> text
"Some text with ***."
```

### automated language detection

- from text:

```python
>>> from safetext import SafeText

>>> eng_text = "This story is about to take a dark turn."

>>> st = SafeText(language=None)
>>> st.set_language_from_text(eng_text)

>>> st.language
'en'
```

- from .srt (subtitle) file:

```python
>>> from safetext import SafeText

>>> turkish_srt_file_path = "turkish.srt"

>>> st = SafeText(language=None)
>>> st.set_language_from_srt(turkish_srt_file_path)

>>> st.language
'tr'
```

## 📜 license

**safetext** is proudly open-source, available under the [MIT License](LICENSE).

## 📞 contact

for inquiries or support, reach out via [email](mailto:support@safevideo.ai) or visit our website [SafeVideo](https://safevideo.ai/).

## 🤝 contribute to safetext

join our mission in refining content moderation!

contribute by:

- **adding new languages**: create a folder with the ISO 639-1 code and include a `words.txt`.
- **enhancing word lists**: improve detection accuracy.
- **sharing feedback**: your ideas can shape `safetext`.

see our [contributing guidelines](CONTRIBUTING.md) for more.

______________________________________________________________________

## 🏆 contributors

meet our awesome contributors who make **safetext** better every day!

<p align="center">
    <a href="https://github.com/safevideo/safetext/graphs/contributors">
      <img src="https://contrib.rocks/image?repo=safevideo/safetext" />
    </a>
</p>

______________________________________________________________________

<div align="center">
  <b>follow us for more!</b>
  <br>
  <a href="https://www.linkedin.com/company/safevideo/">
      <img
        src="https://user-images.githubusercontent.com/44926076/278822352-30e06f9b-1915-4aed-8081-6796432daa7a.png"
        height="32px"
      />
  </a>
  <a href="https://huggingface.co/safevideo">
      <img
        src="https://user-images.githubusercontent.com/34196005/278877706-ed074c9c-0938-48a1-98e8-39a322faf01d.png"
        height="32px"
      />
  </a>
  <a href="https://twitter.com/safevideo_ai">
      <img
        src="https://user-images.githubusercontent.com/34196005/278877049-141925a9-aa1b-4730-829e-74f6d08ee8ca.png"
        height="32px"
      />
  </a>
</div>
