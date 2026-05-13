#!/usr/bin/env python3
"""
GSA FASTQ数据校验工具 - 主程序

用于校验提交至GSA的FASTQ文件，生成详细的校验报告。

使用方法:
    python gsa_validator.py <fastq_file> [options]
    python gsa_validator.py --batch <directory> [options]
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List

# 如果作为脚本直接运行，使用绝对导入
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from validator import GSAFastQValidator, ValidationReport
from bam_validator import GSABAMValidator
from md5_checker import MD5Checker
from report_generator import GSAReportGenerator


def print_error(message: str, verbose: bool = False):
    """统一错误输出"""
    if verbose:
        print(f"❌ 错误: {message}")
    else:
        print(json.dumps({"status": 500, "info": message}, ensure_ascii=False))


def print_report(report: ValidationReport, verbose: bool = False):
    """打印校验报告"""
    if verbose:
        print("\n" + "="*70)
        print(f"文件: {report.file_path}")
        print("="*70)
        print(f"\n{report.summary}\n")

        errors = report.get_errors()
        if errors:
            print("❌ 错误:")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. [{error.check_type}] {error.message}")
                if error.details:
                    for key, value in error.details.items():
                        print(f"     {key}: {value}")
                if error.recommendation:
                    print(f"     建议: {error.recommendation}")
            print()

        warnings = report.get_warnings()
        if warnings:
            print("⚠ 警告:")
            for i, warning in enumerate(warnings, 1):
                print(f"  {i}. [{warning.check_type}] {warning.message}")
                if warning.recommendation:
                    print(f"     建议: {warning.recommendation}")
            print()

        passed = [c for c in report.checks if c.status == "passed"]
        if passed:
            print("✓ 通过的检查:")
            for check in passed:
                print(f"  - [{check.check_type}] ✓ {check.message}")
            print()
    else:
        print(GSAReportGenerator.generate_simple_json(report))


def validate_file(file_path: str, check_casava: bool = False, verbose: bool = False) -> ValidationReport:
    """校验单个文件"""
    path = Path(file_path)
    
    # 判断文件类型
    if path.suffix.lower() == '.bam':
        validator = GSABAMValidator()
    else:
        validator = GSAFastQValidator(check_casava_format=check_casava)
    
    report = validator.validate(file_path)
    print_report(report, verbose)
    
    return report


def batch_validate(directory: str, pattern: str = "*.fastq*", verbose: bool = False):
    """批量校验目录中的文件"""
    dir_path = Path(directory)
    if not dir_path.is_dir():
        print_error(f"{directory} 不是有效的目录", verbose)
        return

    # 查找匹配的文件
    files = list(dir_path.glob(pattern))

    if not files:
        print_error(f"在 {directory} 中未找到匹配 {pattern} 的文件", verbose)
        return

    if verbose:
        print(f"找到 {len(files)} 个文件，开始批量校验...\n")

    results = []
    for file_path in files:
        if verbose:
            print(f"处理: {file_path.name}")
        try:
            report = validate_file(str(file_path), verbose=verbose)
            results.append((file_path, report))
        except Exception as e:
            print_error(f"处理 {file_path.name} 失败: {e}", verbose)
            results.append((file_path, None))

    # 汇总
    if verbose:
        print("\n" + "="*70)
        print("批量校验结果汇总")
        print("="*70)

        passed_count = sum(1 for _, r in results if r and r.is_valid)
        failed_count = len(results) - passed_count

        print(f"总文件数: {len(results)}")
        print(f"通过: {passed_count}")
        print(f"失败: {failed_count}")
        print("="*70)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="GSA FASTQ/BAM 数据校验工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='要校验的 FASTQ 或 BAM 文件路径'
    )
    
    parser.add_argument(
        '--batch', '-b',
        metavar='DIR',
        help='批量校验目录中的所有文件'
    )
    
    parser.add_argument(
        '--pattern', '-p',
        default='*.fastq*',
        help='批量校验时的文件匹配模式（默认: *.fastq*）'
    )
    
    parser.add_argument(
        '--generate-md5', '-g',
        action='store_true',
        help='生成 MD5 校验码文件'
    )
    
    parser.add_argument(
        '--verify-md5', '-v',
        action='store_true',
        help='验证 MD5 校验码'
    )
    
    parser.add_argument(
        '--md5-file', '-m',
        metavar='MD5_FILE',
        help='MD5 校验码文件路径（用于验证）'
    )
    
    parser.add_argument(
        '--json-report', '-j',
        metavar='JSON_REPORT',
        help='生成 JSON 格式的详细报告'
    )
    
    parser.add_argument(
        '--check-casava',
        action='store_true',
        help='检查 Illumina Casava 1.8+ 严格格式（双端数据）'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='详细输出模式'
    )
    
    args = parser.parse_args()
    
    # 如果没有提供文件或目录，显示帮助
    if not args.file and not args.batch:
        parser.print_help()
        return
    
    # 批量处理
    if args.batch:
        batch_validate(args.batch, args.pattern, args.verbose)
        return
    
    # 单个文件处理
    if not os.path.exists(args.file):
        print_error(f"文件不存在: {args.file}", args.verbose)
        sys.exit(1)
    
    # MD5 相关操作
    if args.generate_md5:
        md5_file = MD5Checker.generate_md5_file(args.file)
        print(f"✓ MD5 校验码文件已生成: {md5_file}")
        return
    
    if args.verify_md5:
        success, message = MD5Checker.verify_md5(
            args.file,
            md5_file_path=args.md5_file
        )
        print(message)
        return
    
    # 校验文件
    report = validate_file(args.file, args.check_casava, args.verbose)
    
    # 生成 JSON 报告
    if args.json_report:
        GSAReportGenerator.generate_json_report(report, args.json_report)
        print(f"\n✓ JSON 报告已生成: {args.json_report}")
        print(f"✓ 文本报告已生成: {args.json_report.replace('.json', '.txt')}")
    
    # 退出码
    sys.exit(0 if report.is_valid else 1)


if __name__ == "__main__":
    main()

