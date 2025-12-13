#!/usr/bin/env python3
"""
GSA FASTQ 验证器使用示例

演示如何使用 GSA FASTQ 验证器的各种功能。
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from validator import GSAFastQValidator
from bam_validator import GSABAMValidator
from md5_checker import MD5Checker
from report_generator import GSAReportGenerator


def example_basic_validation():
    """示例1：基本校验"""
    print("=" * 70)
    print("示例1：基本FASTQ文件校验")
    print("=" * 70)
    
    validator = GSAFastQValidator(verbose=True)
    report = validator.validate("example/sample_correct.fastq.gz")
    
    if report.is_valid:
        print("\n✓ 校验通过")
    else:
        print("\n❌ 校验失败")
        for error in report.get_errors():
            print(f"  - {error.message}")


def example_bam_validation():
    """示例2：BAM文件校验"""
    print("\n" + "=" * 70)
    print("示例2：BAM文件校验")
    print("=" * 70)
    
    validator = GSABAMValidator()
    report = validator.validate("example/sample.bam")
    
    if report.is_valid:
        print("\n✓ BAM文件校验通过")
    else:
        print("\n❌ BAM文件校验失败")


def example_md5_operations():
    """示例3：MD5操作"""
    print("\n" + "=" * 70)
    print("示例3：MD5校验码操作")
    print("=" * 70)
    
    file_path = "example/sample_correct.fastq.gz"
    
    # 计算MD5
    md5_value = MD5Checker.calculate_md5(file_path)
    print(f"MD5值: {md5_value}")
    
    # 生成MD5文件
    md5_file = MD5Checker.generate_md5_file(file_path)
    print(f"MD5文件: {md5_file}")
    
    # 验证MD5
    success, message = MD5Checker.verify_md5(file_path, md5_file_path=md5_file)
    print(message)


def example_report_generation():
    """示例4：生成报告"""
    print("\n" + "=" * 70)
    print("示例4：生成GSA就绪报告")
    print("=" * 70)
    
    validator = GSAFastQValidator()
    report = validator.validate("example/sample_correct.fastq.gz")
    
    # 生成JSON报告
    json_data = GSAReportGenerator.generate_json_report(report, "report.json")
    print("✓ JSON报告已生成: report.json")
    print("✓ 文本报告已生成: report.txt")
    
    # 生成人类可读报告
    text_report = GSAReportGenerator.generate_human_readable_report(report)
    print("\n" + text_report)


def example_strict_mode():
    """示例5：严格模式（Casava格式检查）"""
    print("\n" + "=" * 70)
    print("示例5：严格模式（Casava格式检查）")
    print("=" * 70)
    
    validator = GSAFastQValidator(check_casava_format=True)
    report = validator.validate("example/sample_paired_1.fastq.gz")
    
    print_report(report)


def print_report(report):
    """打印报告"""
    print(f"\n{report.summary}")
    errors = report.get_errors()
    if errors:
        print("\n错误:")
        for error in errors:
            print(f"  - {error.message}")


if __name__ == "__main__":
    print("GSA FASTQ 验证器使用示例")
    print("=" * 70)
    print()
    
    # 运行示例（需要相应的测试文件）
    # example_basic_validation()
    # example_bam_validation()
    # example_md5_operations()
    # example_report_generation()
    # example_strict_mode()
    
    print("\n提示: 取消注释上面的示例函数调用来运行示例")

