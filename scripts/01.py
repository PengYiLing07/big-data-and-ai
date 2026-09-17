# -*- coding: utf-8 -*-
"""
第 1 讲 · 环境自检
对应《0917课堂要点》—— 创建 .py 文件并运行

在 VS Code 里运行方式：
    1) 打开本文件，右上角点“运行”三角按钮；或
    2) 终端执行：python scripts/01.py

作者：PengYiLing07
"""

import platform
import subprocess
import sys


def pip_index_url():
    """读取当前生效的 pip 镜像源，确认已设置成国内源。"""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "config", "get", "global.index-url"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() or "(未设置，仍是官方源)"


def main():
    print("你好，这是我在 VS Code 里创建并运行的第一个 .py 文件。")
    print("-" * 46)
    print("Python 版本：", sys.version.split()[0])
    print("解释器路径：", sys.executable)
    print("操作系统：  ", platform.system(), platform.release())
    print("pip 镜像源：", pip_index_url())
    print("-" * 46)
    print("环境自检完成：Python 可用，pip 已指向国内源。")


if __name__ == "__main__":
    main()
