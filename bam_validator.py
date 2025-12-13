#!/usr/bin/env python3
"""
GSA BAM文件校验器

根据GSA要求校验BAM文件格式和内容。
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

try:
    from .validator import ValidationCheck, ValidationReport, ValidationSeverity
except ImportError:
    from validator import ValidationCheck, ValidationReport, ValidationSeverity


class GSABAMValidator:
    """GSA BAM文件校验器"""
    
    def __init__(self):
        """初始化BAM校验器"""
        self.checks: List[ValidationCheck] = []
        self.samtools_available = self._check_samtools()
        self.pysam_available = self._check_pysam()
    
    def _check_samtools(self) -> bool:
        """检查samtools是否可用"""
        try:
            result = subprocess.run(
                ['samtools', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _check_pysam(self) -> bool:
        """检查pysam是否可用"""
        try:
            import pysam
            return True
        except ImportError:
            return False
    
    def validate(self, file_path: str) -> ValidationReport:
        """
        校验BAM文件
        
        Args:
            file_path: BAM文件路径
            
        Returns:
            ValidationReport对象
        """
        self.checks = []
        file_path = str(file_path)
        
        # 1. 文件存在性检查
        if not os.path.exists(file_path):
            self.checks.append(ValidationCheck(
                check_type="file_existence",
                severity=ValidationSeverity.ERROR,
                status="failed",
                message=f"文件不存在: {file_path}"
            ))
            return ValidationReport(
                file_path=file_path,
                checks=self.checks,
                is_valid=False,
                summary=f"❌ {file_path}: 文件不存在"
            )
        
        # 2. 文件扩展名检查
        path = Path(file_path)
        if path.suffix.lower() == '.bam':
            self.checks.append(ValidationCheck(
                check_type="file_extension",
                severity=ValidationSeverity.ERROR,
                status="passed",
                message="文件扩展名正确: .bam"
            ))
        else:
            self.checks.append(ValidationCheck(
                check_type="file_extension",
                severity=ValidationSeverity.ERROR,
                status="failed",
                message=f"文件扩展名不正确: {path.suffix}，应为 .bam"
            ))
        
        # 3. 文件名规范检查（与FASTQ相同）
        filename = path.name
        forbidden_chars = [' ', '-', '(', ')', '/', '\\']
        has_forbidden = any(char in filename for char in forbidden_chars)
        
        if not has_forbidden:
            self.checks.append(ValidationCheck(
                check_type="filename_format",
                severity=ValidationSeverity.ERROR,
                status="passed",
                message=f"文件名符合规范: {filename}"
            ))
        else:
            self.checks.append(ValidationCheck(
                check_type="filename_format",
                severity=ValidationSeverity.ERROR,
                status="failed",
                message="文件名包含禁止字符",
                recommendation="请重命名文件，移除空格、连字符、括号等禁止字符"
            ))
        
        # 4. BAM文件结构完整性检查
        self._check_bam_structure(file_path)
        
        # 5. 索引文件检查
        self._check_index_file(file_path)
        
        # 汇总结果
        errors = [c for c in self.checks if c.severity == ValidationSeverity.ERROR and c.status == "failed"]
        is_valid = len(errors) == 0
        
        if is_valid:
            summary = f"✓ {os.path.basename(file_path)}: BAM文件校验通过"
        else:
            summary = f"❌ {os.path.basename(file_path)}: 发现 {len(errors)} 个错误"
        
        return ValidationReport(
            file_path=file_path,
            checks=self.checks,
            is_valid=is_valid,
            summary=summary
        )
    
    def _check_bam_structure(self, file_path: str):
        """检查BAM文件结构完整性"""
        if self.samtools_available:
            # 使用 samtools quickcheck
            try:
                result = subprocess.run(
                    ['samtools', 'quickcheck', file_path],
                    capture_output=True,
                    timeout=60
                )
                if result.returncode == 0:
                    self.checks.append(ValidationCheck(
                        check_type="bam_structure",
                        severity=ValidationSeverity.ERROR,
                        status="passed",
                        message="BAM文件结构完整（samtools验证）"
                    ))
                else:
                    self.checks.append(ValidationCheck(
                        check_type="bam_structure",
                        severity=ValidationSeverity.ERROR,
                        status="failed",
                        message="BAM文件结构可能损坏",
                        recommendation="请使用 samtools 修复或重新生成BAM文件"
                    ))
            except subprocess.TimeoutExpired:
                self.checks.append(ValidationCheck(
                    check_type="bam_structure",
                    severity=ValidationSeverity.WARNING,
                    status="failed",
                    message="BAM文件检查超时"
                ))
        elif self.pysam_available:
            # 使用 pysam
            try:
                import pysam
                with pysam.AlignmentFile(file_path, 'rb') as bam:
                    # 尝试读取第一个记录
                    try:
                        next(bam)
                        self.checks.append(ValidationCheck(
                            check_type="bam_structure",
                            severity=ValidationSeverity.ERROR,
                            status="passed",
                            message="BAM文件结构完整（pysam验证）"
                        ))
                    except StopIteration:
                        self.checks.append(ValidationCheck(
                            check_type="bam_structure",
                            severity=ValidationSeverity.WARNING,
                            status="failed",
                            message="BAM文件为空"
                        ))
            except Exception as e:
                self.checks.append(ValidationCheck(
                    check_type="bam_structure",
                    severity=ValidationSeverity.ERROR,
                    status="failed",
                    message=f"BAM文件结构错误: {str(e)}"
                ))
        else:
            self.checks.append(ValidationCheck(
                check_type="bam_structure",
                severity=ValidationSeverity.WARNING,
                status="failed",
                message="无法检查BAM文件结构（需要安装 samtools 或 pysam）",
                recommendation="请安装 samtools 或 pysam: pip install pysam"
            ))
    
    def _check_index_file(self, file_path: str):
        """检查BAM索引文件"""
        index_file = file_path + '.bai'
        if os.path.exists(index_file):
            self.checks.append(ValidationCheck(
                check_type="bam_index",
                severity=ValidationSeverity.INFO,
                status="passed",
                message="BAM索引文件存在"
            ))
        else:
            self.checks.append(ValidationCheck(
                check_type="bam_index",
                severity=ValidationSeverity.INFO,
                status="failed",
                message="BAM索引文件不存在（可选）",
                recommendation="可以使用 samtools index 创建索引文件"
            ))

