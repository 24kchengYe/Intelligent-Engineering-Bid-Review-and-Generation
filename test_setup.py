"""
环境配置测试脚本
运行此脚本以验证系统配置是否正确
"""

import sys
import os

def test_python_version():
    """测试 Python 版本"""
    print("1. 检查 Python 版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python 版本过低: {version.major}.{version.minor}.{version.micro}")
        print(f"   需要 Python 3.9 或更高版本")
        return False

def test_dependencies():
    """测试依赖包"""
    print("\n2. 检查依赖包...")
    dependencies = [
        'streamlit',
        'anthropic',
        'fitz',  # PyMuPDF
        'docx',
        'openpyxl',
        'pandas',
        'sqlalchemy',
        'dotenv'
    ]

    all_ok = True
    for dep in dependencies:
        try:
            if dep == 'fitz':
                import fitz
                print(f"   ✅ PyMuPDF (fitz)")
            elif dep == 'docx':
                import docx
                print(f"   ✅ python-docx")
            elif dep == 'dotenv':
                from dotenv import load_dotenv
                print(f"   ✅ python-dotenv")
            else:
                __import__(dep)
                print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} 未安装")
            all_ok = False

    return all_ok

def test_env_file():
    """测试环境配置文件"""
    print("\n3. 检查环境配置...")
    if not os.path.exists('.env'):
        print("   ❌ .env 文件不存在")
        print("   请复制 .env.example 为 .env 并配置 API Key")
        return False

    print("   ✅ .env 文件存在")

    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        print("   ⚠️  ANTHROPIC_API_KEY 未配置或使用默认值")
        print("   请在 .env 文件中填入有效的 API Key")
        return False

    print("   ✅ ANTHROPIC_API_KEY 已配置")
    return True

def test_api_connection():
    """测试 API 连接"""
    print("\n4. 测试 Claude API 连接...")
    try:
        from modules.ai_service import ClaudeService

        # 尝试创建服务实例
        service = ClaudeService()
        print("   ✅ API 服务初始化成功")

        # 可选：测试简单调用（消耗少量 token）
        print("   正在测试 API 调用（这会消耗少量 token）...")
        response = service.chat("请回复：OK")
        print(f"   ✅ API 调用成功，响应: {response[:50]}...")
        return True

    except Exception as e:
        print(f"   ❌ API 连接失败: {str(e)}")
        return False

def test_directories():
    """测试目录结构"""
    print("\n5. 检查目录结构...")
    directories = ['modules', 'uploads', 'data']

    all_ok = True
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"   ✅ 创建目录: {directory}/")
            except Exception as e:
                print(f"   ❌ 无法创建目录 {directory}/: {str(e)}")
                all_ok = False
        else:
            print(f"   ✅ {directory}/")

    return all_ok

def main():
    """主测试函数"""
    print("=" * 50)
    print("  智能标书审查系统 - 环境配置测试")
    print("=" * 50)

    results = []

    # 运行所有测试
    results.append(("Python 版本", test_python_version()))
    results.append(("依赖包", test_dependencies()))
    results.append(("目录结构", test_directories()))
    results.append(("环境配置", test_env_file()))

    # 只有前面都通过才测试 API
    if all(r[1] for r in results):
        results.append(("API 连接", test_api_connection()))

    # 总结
    print("\n" + "=" * 50)
    print("  测试总结")
    print("=" * 50)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！系统配置正确。")
        print("\n可以运行以下命令启动系统：")
        print("  streamlit run app.py")
        print("\n或双击运行 start.bat (Windows) / start.sh (Mac/Linux)")
    else:
        print("⚠️  部分测试未通过，请根据上述提示修复问题。")
        print("\n常见问题解决：")
        print("1. 依赖包缺失 → 运行: pip install -r requirements.txt")
        print("2. API Key 未配置 → 编辑 .env 文件，填入 ANTHROPIC_API_KEY")
        print("3. API 连接失败 → 检查网络连接和 API Key 是否有效")
    print("=" * 50)

    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())
