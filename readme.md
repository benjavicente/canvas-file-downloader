# Canvas File Downloader

Simple file downloader for Canvas of Instructure.

Features:

- Downloads only the courses marked as favorites.
- If a file already exists, it's omitted (marked with `*`)

Usage:

```bash
python canvas.py YOUR-TOKEN
```

Where `YOUR-TOKEN` is the token access of Canvas.
You can get the access token from [here][get_token].

Other related projects:

- [CanvasSync](https://github.com/perslev/CanvasSync)

[get_token]: https://cursos.canvas.uc.cl/profile/settings#access_tokens
