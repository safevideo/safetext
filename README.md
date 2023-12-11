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

**Expand. Detect. Protect.**

- **Multi-language**: Supports five languages with ease of expansion.
- **Automated**: Smart language detection for quick setup.
- **Simple**: Easy to use and integrate.

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

safetext is available under the [MIT License](LICENSE).

## 📞 contact

For more information, support, or questions, please contact:

- **Email**: [support@safevideo.ai](mailto:support@safevideo.ai)
- **Website**: [SafeVideo](https://safevideo.ai/)

## 🤝 contribute to safetext

**join us in shaping the future of content moderation!**

safetext is an MIT-licensed open-source project. Your contributions in adding new languages, improving existing word lists, or sharing ideas help us grow stronger.

**How to Contribute?**

- **New Languages**: Add by creating a folder with the ISO 639-1 code and a `words.txt`.
- **Enhance Lists**: Make our profanity detection more robust.
- **Share Ideas**: Suggestions and feedback are always welcome.

check our [contributing guidelines](CONTRIBUTING.md) to get started.

______________________________________________________________________

## 🏆 our contributors

we value each contribution. meet our awesome contributors who make **safetext** better every day!

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
