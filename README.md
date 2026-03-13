# 党巍内容库

这个仓库现在只做一件事：存放可直接被博客读取的原版文章内容。

仓库里不再放抓取脚本、测试代码、原始导出数据、公众号 HTML 排版稿、小红书拆分稿等工具型文件。这里就是一个纯内容库。

## 当前目录结构

```text
.
├── YYYY/
│   └── MM/
│       └── DD/
│           ├── article.md
│           └── images/
│               ├── cover.jpg / cover.png
│               └── image-01.png ...
├── metadata.json
├── README.md
└── .gitignore
```

### 目录说明

- `YYYY/MM/DD/article.md`
  文章正文，使用标准 Markdown 保存。
- `YYYY/MM/DD/images/`
  文章本地图片目录。
  `cover.*` 用作封面图，`image-*.*` 是正文配图。
- `metadata.json`
  文章索引文件，博客或其他内容消费端优先读这个文件。

## 文章组织规则

每篇文章固定放在一个日期目录下，例如：

```text
2025/11/04/
├── article.md
└── images/
    ├── cover.jpg
    └── image-01.png
```

正文里的图片统一使用相对路径，例如：

```md
![](images/image-01.png)
```

这样博客在读取 `article.md` 时，只要把文章目录当成资源根目录，就能正确解析正文配图。

## metadata.json 怎么读

`metadata.json` 的顶层结构如下：

```json
{
  "version": "1.0",
  "lastUpdated": "2026-03-12T12:45:00+08:00",
  "articles": [
    {
      "id": "2026-03-10-openclaw-deployment",
      "date": "2026-03-10",
      "title": "OpenClaw 部署一个月踩坑实录：从云服务器到本地 Mac",
      "path": "2026/03/10/article.md",
      "cover": "2026/03/10/images/cover.png"
    }
  ]
}
```

### 核心字段

- `id`
  文章唯一标识。
- `date`
  发布日期，格式固定为 `YYYY-MM-DD`。
- `title`
  文章标题。
- `path`
  Markdown 正文的相对路径。
- `cover`
  封面图的相对路径。
- `source_url`
  可选字段，记录原始文章来源链接。

### 推荐读取方式

博客站点建议按下面的顺序读取：

1. 先读取 `metadata.json`
2. 遍历 `articles`
3. 用每条记录里的 `path` 读取正文
4. 用 `cover` 读取封面图
5. 渲染正文时，保持 Markdown 内相对图片路径不变

如果你的站点构建器会把 Markdown 文件复制到其他位置，记得同时把对应目录下的 `images/` 一起带走。

## 设计原则

- 仓库只保留内容成品，不保留采集和转换过程
- 正文优先保证可读性，统一使用标准 Markdown
- 图片优先本地化，避免正文依赖外部图床
- 目录结构固定，方便静态站点和脚本稳定读取

## 仓库地址

- GitHub: [DwDestiny/dang-wei-content](https://github.com/DwDestiny/dang-wei-content)
- GitHub Pages: [dwdestiny.github.io/dang-wei-content](https://dwdestiny.github.io/dang-wei-content/)
