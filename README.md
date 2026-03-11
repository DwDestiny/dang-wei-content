# 党巍的内容仓库

博客、公众号、小红书分发中心

## 目录结构

```
content/
├── YYYY/                           # 年份
│   └── MM/                         # 月份
│       └── DD/                     # 日期
│           ├── article.md          # 原版 Markdown
│           ├── images/             # 原始配图
│           ├── wechat/             # 公众号版本
│           │   ├── article.html    # HTML 排版
│           │   └── images/         # 微信素材库链接映射
│           └── xiaohongshu/        # 小红书版本
│               └── page-N.png      # 长图文分页
├── metadata.json                   # 文章索引
└── README.md                       # 本文件
```

## 工作流程

1. 写初稿 → 讨论定稿 → 推送原版
2. 处理各版本：
   - 上传图片到图床 → 更新 Markdown 远程链接
   - 上传图片到微信素材库 → 生成 HTML 公众号版
   - 排版 → 生成长图小红书版
3. 推送各版本到 GitHub
4. 分发到各平台

## 访问地址

- GitHub: https://github.com/DwDestiny/dang-wei-content
- GitHub Pages: https://dwdestiny.github.io/dang-wei-content/
