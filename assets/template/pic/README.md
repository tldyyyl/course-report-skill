# 图片目录

此目录用于存放课程报告中使用的图片。

## 学校Logo

如果需要在封面显示学校logo：

1. 将学校logo图片命名为 `logo.pdf`
2. 放在此目录下
3. 在 `main.tex` 中取消注释 `\showlogo` 命令

支持的图片格式：PDF、PNG、JPG、JPEG。用于打印时优先使用 PDF 矢量图片。

## 其他图片

报告中引用的其他图片也可以放在此目录，使用方式：

```latex
\begin{figure}[h]
  \includegraphics[width=0.8\textwidth]{pic/your-image.png}
  \caption{图片说明}
  \label{fig:your-label}
\end{figure}
```
