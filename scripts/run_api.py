"""API启动脚本"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    import argparse

    parser = argparse.ArgumentParser(description="启动物业大模型API服务")
    parser.add_argument("--host", default="0.0.0.0", help="服务地址")
    parser.add_argument("--port", type=int, default=8000, help="服务端口")
    parser.add_argument("--reload", action="store_true", help="启用热重载")
    parser.add_argument("--log-level", default="info", help="日志级别")

    args = parser.parse_args()

    # 导入并启动服务
    from api.main import app
    import uvicorn

    print(f"""
========================================
  物业大模型应用平台 API
========================================
  服务地址: http://{args.host}:{args.port}
  API文档:  http://{args.host}:{args.port}/docs
  健康检查: http://{args.host}:{args.port}/health
========================================
    """)

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )


if __name__ == "__main__":
    main()
