# 生产环境配置 - 严格禁止自动生成测试数据

class ProductionConfig:
    # 服务器配置
    HOST = "0.0.0.0"
    PORT = 8000
    
    # 数据库配置
    DATABASE_URL = "proxy.db"
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FILE = "proxy.log"
    
    # 安全配置
    API_KEY_LENGTH = 64
    RATE_LIMIT = 60  # 每分钟请求数
    
    # 监控配置
    MONITORING_ENABLED = True
    CHECK_INTERVAL = 60  # 秒
    ALERT_THRESHOLD = 5
    
    # ===== 严格禁止自动生成测试数据 =====
    # 这些配置必须设置为False，禁止系统自动生成任何测试数据
    AUTO_GENERATE_TEST_DATA = False  # 禁止自动生成测试数据
    MOCK_DATA_ENABLED = False  # 禁止使用模拟数据
    DEMO_MODE = False  # 禁止演示模式
    TEST_MODE = False  # 禁止测试模式
    
    # 数据验证配置 - 确保只有真实业务才能产生数据
    REQUIRE_REAL_PAYMENT = True  # 必须真实支付才能生成订单
    REQUIRE_REAL_API_CALL = True  # 必须真实调用上游API才能生成请求记录
    REQUIRE_REAL_USER = True  # 必须真实用户才能生成数据
    
    # 上游渠道配置 - 已配置硅基流动真实API密钥
    UPSTREAM = {
        "siliconflow": {
            "url": "https://api.siliconflow.cn/v1",
            "api_key": "sk-olvfymjregzucoaqmgirgbsahiptcafpmdtenjumerlzvtem"  # 硅基流动真实API密钥
        },
        "openai": {
            "url": "https://api.openai.com/v1",
            "api_key": "YOUR_REAL_OPENAI_API_KEY_HERE"  # 必须替换为真实API密钥
        },
        "anthropic": {
            "url": "https://api.anthropic.com/v1",
            "api_key": "YOUR_REAL_ANTHROPIC_API_KEY_HERE"  # 必须替换为真实API密钥
        },
        "groq": {
            "url": "https://api.groq.com/openai/v1",
            "api_key": "YOUR_REAL_GROQ_API_KEY_HERE"  # 必须替换为真实API密钥
        }
    }
    
    # 产品价格表
    PRODUCTS = {
        "gpt-4o": {
            "100万token": 30,
            "500万token": 140,
            "1000万token": 270
        },
        "claude-3.5": {
            "100万token": 25,
            "500万token": 115,
            "1000万token": 220
        },
        "包月会员": {
            "基础版": 50,
            "高级版": 99
        }
    }
    
    # 佣金配置
    AFFILIATE_COMMISSION_RATE = 0.2  # 20%

class DevelopmentConfig:
    # 开发环境配置 - 同样禁止自动生成测试数据
    HOST = "127.0.0.1"
    PORT = 8000
    
    # 数据库配置
    DATABASE_URL = "proxy_dev.db"
    
    # 日志配置
    LOG_LEVEL = "DEBUG"
    LOG_FILE = "proxy_dev.log"
    
    # 安全配置
    API_KEY_LENGTH = 64
    RATE_LIMIT = 100  # 每分钟请求数
    
    # 监控配置
    MONITORING_ENABLED = True
    CHECK_INTERVAL = 30  # 秒
    ALERT_THRESHOLD = 3
    
    # ===== 严格禁止自动生成测试数据 =====
    AUTO_GENERATE_TEST_DATA = False  # 禁止自动生成测试数据
    MOCK_DATA_ENABLED = False  # 禁止使用模拟数据
    DEMO_MODE = False  # 禁止演示模式
    TEST_MODE = False  # 禁止测试模式
    
    # 数据验证配置 - 确保只有真实业务才能产生数据
    REQUIRE_REAL_PAYMENT = True  # 必须真实支付才能生成订单
    REQUIRE_REAL_API_CALL = True  # 必须真实调用上游API才能生成请求记录
    REQUIRE_REAL_USER = True  # 必须真实用户才能生成数据
    
    # 上游渠道配置
    UPSTREAM = {
        "openai": {
            "url": "https://api.openai.com/v1",
            "api_key": "YOUR_REAL_OPENAI_API_KEY_HERE"  # 必须替换为真实API密钥
        },
        "anthropic": {
            "url": "https://api.anthropic.com/v1",
            "api_key": "YOUR_REAL_ANTHROPIC_API_KEY_HERE"  # 必须替换为真实API密钥
        },
        "groq": {
            "url": "https://api.groq.com/openai/v1",
            "api_key": "YOUR_REAL_GROQ_API_KEY_HERE"  # 必须替换为真实API密钥
        }
    }
    
    # 产品价格表
    PRODUCTS = {
        "gpt-4o": {
            "100万token": 30,
            "500万token": 140,
            "1000万token": 270
        },
        "claude-3.5": {
            "100万token": 25,
            "500万token": 115,
            "1000万token": 220
        },
        "包月会员": {
            "基础版": 50,
            "高级版": 99
        }
    }
    
    # 佣金配置
    AFFILIATE_COMMISSION_RATE = 0.2  # 20%

# 根据环境选择配置
import os

# 强制设置为生产环境，禁止测试模式
os.environ["ENVIRONMENT"] = "production"
Config = ProductionConfig
