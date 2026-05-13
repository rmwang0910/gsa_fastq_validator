#!/usr/bin/env python3
"""
GSA就绪报告生成器

生成JSON和人类可读格式的校验报告，直接映射GSA官方条款编号。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

try:
    from .validator import ValidationReport, ValidationCheck, ValidationSeverity
except ImportError:
    from validator import ValidationReport, ValidationCheck, ValidationSeverity


# GSA条款编号映射
GSA_REQUIREMENT_MAP = {
    "file_existence": "GSA-REQ-001",
    "file_extension": "GSA-REQ-002",
    "compression_format": "GSA-REQ-003",
    "filename_format": "GSA-REQ-004",
    "fastq_structure": "GSA-REQ-005",
    "base_content": "GSA-REQ-006",
    "quality_scores": "GSA-REQ-007",
    "paired_reads": "GSA-REQ-008",
    "casava_format": "GSA-REQ-009",
    "compression_integrity": "GSA-REQ-010",
    "bam_structure": "GSA-REQ-011",
}


class GSAReportGenerator:
    """GSA就绪报告生成器"""
    
    @staticmethod
    def generate_json_report(report: ValidationReport, output_path: str) -> Dict[str, Any]:
        """
        生成JSON格式的详细报告
        
        Args:
            report: ValidationReport对象
            output_path: 输出JSON文件路径
            
        Returns:
            JSON数据字典
        """
        errors = report.get_errors()
        warnings = report.get_warnings()
        passed = [c for c in report.checks if c.status == "passed"]
        
        json_data = {
            "file_path": report.file_path,
            "file_name": Path(report.file_path).name,
            "validation_time": datetime.now().isoformat(),
            "is_gsa_ready": report.is_valid,
            "summary": report.summary,
            "statistics": {
                "total_checks": len(report.checks),
                "passed": len(passed),
                "warnings": len(warnings),
                "errors": len(errors)
            },
            "checks": []
        }
        
        for check in report.checks:
            check_data = {
                "check_type": check.check_type,
                "gsa_requirement": GSA_REQUIREMENT_MAP.get(check.check_type, "N/A"),
                "severity": check.severity.value,
                "status": check.status,
                "message": check.message
            }
            
            if check.details:
                check_data["details"] = check.details
            
            if check.recommendation:
                check_data["recommendation"] = check.recommendation
            
            json_data["checks"].append(check_data)
        
        # 保存JSON文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        # 同时生成人类可读的文本报告
        text_report_path = output_path.replace('.json', '.txt')
        text_report = GSAReportGenerator.generate_human_readable_report(report)
        with open(text_report_path, 'w', encoding='utf-8') as f:
            f.write(text_report)
        
        return json_data
    
    @staticmethod
    def generate_human_readable_report(report: ValidationReport) -> str:
        """
        生成人类可读的文本报告
        
        Args:
            report: ValidationReport对象
            
        Returns:
            文本报告字符串
        """
        lines = []
        lines.append("=" * 70)
        lines.append("GSA FASTQ/BAM 数据校验报告")
        lines.append("=" * 70)
        lines.append(f"文件: {report.file_path}")
        lines.append(f"文件名: {Path(report.file_path).name}")
        lines.append(f"校验时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append(report.summary)
        lines.append("")
        
        errors = report.get_errors()
        warnings = report.get_warnings()
        passed = [c for c in report.checks if c.status == "passed"]
        
        lines.append("统计信息:")
        lines.append(f"  总检查项: {len(report.checks)}")
        lines.append(f"  通过: {len(passed)}")
        lines.append(f"  警告: {len(warnings)}")
        lines.append(f"  错误: {len(errors)}")
        lines.append("")
        
        if passed:
            lines.append("✓ 通过的检查:")
            for check in passed:
                gsa_req = GSA_REQUIREMENT_MAP.get(check.check_type, "")
                req_str = f" [{gsa_req}]" if gsa_req else ""
                lines.append(f"  - [{check.check_type}]{req_str} ✓ {check.message}")
            lines.append("")
        
        if warnings:
            lines.append("⚠ 警告:")
            for check in warnings:
                gsa_req = GSA_REQUIREMENT_MAP.get(check.check_type, "")
                req_str = f" [{gsa_req}]" if gsa_req else ""
                lines.append(f"  - [{check.check_type}]{req_str} ⚠ {check.message}")
                if check.recommendation:
                    lines.append(f"    建议: {check.recommendation}")
            lines.append("")
        
        if errors:
            lines.append("❌ 错误:")
            for check in errors:
                gsa_req = GSA_REQUIREMENT_MAP.get(check.check_type, "")
                req_str = f" [{gsa_req}]" if gsa_req else ""
                lines.append(f"  - [{check.check_type}]{req_str} ❌ {check.message}")
                if check.recommendation:
                    lines.append(f"    建议: {check.recommendation}")
            lines.append("")
        
        lines.append("=" * 70)
        lines.append("GSA就绪状态: " + ("✅ 是" if report.is_valid else "❌ 否"))
        lines.append("=" * 70)

        return "\n".join(lines)

    @staticmethod
    def generate_simple_json(report: ValidationReport) -> str:
        """
        生成简洁的JSON状态输出

        Args:
            report: ValidationReport对象

        Returns:
            JSON字符串
        """
        if report.is_valid:
            return json.dumps({"status": 200}, ensure_ascii=False)
        else:
            errors = report.get_errors()
            error_messages = [e.message for e in errors]
            info = "; ".join(error_messages) if error_messages else "校验失败"
            return json.dumps({"status": 500, "info": info}, ensure_ascii=False)

