# Canvas File Downloader

Simple file downloader for Canvas of Instructure.

Features:

- Downloads all courses or only the ones marked as favorites
- Download from Modules, Files or both
- If a file already exists, it's omitted
- If a Google Drive file is linked, it will be downloaded

Usage:

First, download the requirements with:

```shell
python -m pip install -r requirements.txt
```

then, run the module with:

```shell
python canvas.py YOUR-TOKEN CANVAS-DOMAIN
```

Where:

- `YOUR-TOKEN` is the token access of Canvas, generated [here][get_token].
- `CANVAS-DOMAIN` the Canvas domain where files will be downloaded.

Optional parameters:

- `-f FROM`: where to download the files, can be modules,
  folders or both (default: `both`).
- `-o DIR`: name of the output directory (default: `CanvasFiles`).
- `--all`: include all courses instead of only favorites.

Related projects:

- [CanvasSync](https://github.com/perslev/CanvasSync)
- [CanvasAPI](https://github.com/ucfopen/canvasapi)
- [Canvas LMS](https://github.com/instructure/canvas-lms)

[get_token]: https://cursos.canvas.uc.cl/profile/settings#access_tokens
