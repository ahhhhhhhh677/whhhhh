@echo off

rem 启动AI服务中转代理系统
echo 正在启动AI服务中转代理系统...
echo 服务将在 http://0.0.0.0:8000 上运行
echo 管理界面：http://localhost:8000
echo 按 Ctrl+C 停止服务

python app_proxy.py