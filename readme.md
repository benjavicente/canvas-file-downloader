# Canvas File Downloader

Simple file downloader for Canvas of Instructure.

Features:

- Downloads all courses or only the ones marked as favorites
- If a file already exists, it's omitted

Usage:

First, download the requirements with:

```shell
python -m pip install -r requirements.txt
```

then, run the module with:

```shell
python canvas.py YOUR-TOKEN CANVAS-URL
```

Where `YOUR-TOKEN` is the token access of Canvas, and
`CANVAS-URL` the Canvas URL.
You can get the access token from [here][get_token].

Related projects:

- [CanvasSync](https://github.com/perslev/CanvasSync)
- [CanvasAPI](https://github.com/ucfopen/canvasapi)
- [Canvas LMS](https://github.com/instructure/canvas-lms)

[get_token]: https://cursos.canvas.uc.cl/profile/settings#access_tokens
