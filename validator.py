#!/usr/bin/env python3
"""
GSA FASTQ文件校验器

根据GSA (Genome Sequence Archive) 官方要求校验FASTQ文件。

校验项：
1. 文件格式（扩展名、压缩格式）
2. FASTQ结构（4行/读取）
3. 读取标识符格式（@开头）
4. 碱基序列格式（ACGTNactgn.）
5. 质量评分格式（Phred 33/64）
6. 配对读取命名规范
7. 文件命名规范（无禁止字符）
"""

import os
import re
import gzip
import bz2
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class ValidationSeverity(Enum):
    """校验严重程度"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationCheck:
    """单个校验结果"""
    check_type: str
    severity: ValidationSeverity
    status: str  # "passed" or "failed"
    message: str
    details: Optional[Dict] = None
    recommendation: Optional[str] = None


@dataclass
class ValidationReport:
    """校验报告"""
    file_path: str
    checks: List[ValidationCheck]
    is_valid: bool
    summary: str
    
    def get_errors(self) -> List[ValidationCheck]:
        """获取所有错误"""
        return [c for c in self.checks if c.severity == ValidationSeverity.ERROR and c.status == "failed"]
    
    def get_warnings(self) -> List[ValidationCheck]:
        """获取所有警告"""
        return [c for c in self.checks if c.severity == ValidationSeverity.WARNING and c.status == "failed"]


class GSAFastQValidator:
    """GSA FASTQ文件校验器"""
    
    # GSA允许的压缩格式
    ALLOWED_COMPRESSION = ['.gz', '.bz2']
    
    # GSA禁止的文件名字符（不包括扩展名中的句点）
    FORBIDDEN_CHARS = [' ', '-', '(', ')', '/', '\\']
    
    # 碱基序列正则表达式（GSA标准）- 已包含点号.
    BASE_PATTERN = re.compile(r'^([ACGTNactgn.]*?)$')
    
    # 配对读取后缀模式
    PAIRED_SUFFIX_PATTERNS = [
        re.compile(r'[._]([12]|R[12]|fwd|rev|forward|reverse)\.(fastq|fq)', re.IGNORECASE),
        re.compile(r'/[12]$')  # 读取名称中的/1或/2
    ]
    
    # Illumina Casava 1.8+ 严格格式正则表达式（GSA要求）
    # 格式: @instrument:run_id:flowcell_id:lane:tile:x:y read:filtered:control:index
    ILLUMINA_CASAVA_PATTERN = re.compile(
        r'^@([a-zA-Z0-9_-]+:[0-9]+:[a-zA-Z0-9]+:[0-9]+:[0-9]+:[0-9-]+:[0-9-]+) ([12]):[YN]:[0-9]*[02468]:[ACGTN]+$'
    )
    
    def __init__(self, strict_mode: bool = True, check_casava_format: bool = False):
        """
        初始化校验器
        
        Args:
            strict_mode: 严格模式，启用所有校验项
            check_casava_format: 是否检查Illumina Casava 1.8+严格格式（双端数据）
        """
        self.strict_mode = strict_mode
        self.check_casava_format = check_casava_format
        self.checks: List[ValidationCheck] = []
    
    def validate(self, file_path: str) -> ValidationReport:
        """
        校验FASTQ文件
        
        Args:
            file_path: FASTQ文件路径
            
        Returns:
            ValidationReport对象
        """
        self.checks = []
        file_path = str(file_path)
        
        # 1. 文件存在性检查
        self._check_file_existence(file_path)
        
        # 如果文件不存在，直接返回
        if not os.path.exists(file_path):
            return ValidationReport(
                file_path=file_path,
                checks=self.checks,
                is_valid=False,
                summary=f"❌ {file_path}: 文件不存在"
            )
        
        # 2. 文件扩展名检查
        self._check_file_extension(file_path)
        
        # 3. 压缩格式检查
        self._check_compression_format(file_path)
        
        # 4. 文件名规范检查
        self._check_filename_format(file_path)
        
        # 5. 压缩文件完整性检查
        self._check_compression_integrity(file_path)
        
        # 6. FASTQ结构检查
        self._check_fastq_structure(file_path)
        
        # 7. 碱基序列格式检查
        self._check_base_content(file_path)
        
        # 8. 质量评分格式检查
        self._check_quality_scores(file_path)
        
        # 9. Casava格式检查（可选）
        if self.check_casava_format:
            self._check_casava_format(file_path)
        
        # 汇总结果
        errors = self.get_errors()
        warnings = self.get_warnings()
        passed = [c for c in self.checks if c.status == "passed"]
        
        is_valid = len(errors) == 0
        
        if is_valid:
            summary = f"✓ {os.path.basename(file_path)}: 所有校验通过"
        else:
            summary = f"❌ {os.path.basename(file_path)}: 发现 {len(errors)} 个错误"
        
        return ValidationReport(
            file_path=file_path,
            checks=self.checks,
            is_valid=is_valid,
            summary=summary
        )
    
    def _check_file_existence(self, file_path: str):
        """检查文件是否存在且可读"""
        if os.path.exists(file_path) and os.access(file_path, os.R_OK):
            self.checks.append(ValidationCheck(
                check_type="file_existence",
                severity=ValidationSeverity.ERROR,
                status="passed",
                message=f"文件存在且可读: {file_path}"
            ))
        else:
            self.checks.append(ValidationCheck(
                check_type="file_existence",
                severity=ValidationSeverity.ERROR,
                status="failed",
                message=f"文件不存在或不可读: {file_path}",
                recommendation="请检查文件路径是否正确"
            ))
    
    def _check_file_extension(self, file_path: str):
        """检查文件扩展名"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        # 处理 .fastq.gz 或 .fq.gz 的情况
        if ext in ['.gz', '.bz2']:
            stem = path.stem
            if stem.endswith('.fastq') or stem.endswith('.fq'):
                self.checks.append(ValidationCheck(
                    check_type="file_extension",
                    severity=ValidationSeverity.ERROR,
                    status="passed",
                    message=f"文件扩展名正确: {path.name}"
                ))
                return
        
        if ext in ['.fastq', '.fq'] or (ext in ['.gz', '.bz2'] and path.stem.endswith(('.fastq', '.fq'))):
            self.checks.append(ValidationCheck(
                check_type="file_extension",
                severity=ValidationSeverity.ERROR,
                status="passed",
                message=f"文件扩展名正确: {path.name}"
            ))
        else:
            self.checks.append(ValidationCheck(
                check_type="file_extension",
                severity=ValidationSeverity.ERROR,
                status="failed",
                message=f"文件扩展名不正确: {ext}，应为 .fastq 或 .fq",
                recommendation="请将文件重命名为 .fastq 或 .fq 格式"
            ))
    
    def _check_compression_format(self, file_path: str):
        """检查压缩格式"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext in self.ALLOWED_COMPRESSION:
            self.checks.append(ValidationCheck(
                check_type="compression_format",
                severity=ValidationSeverity.ERROR,
                status="passed",
                message=f"压缩格式正确: {ext}"
            ))
        elif ext in ['.fastq', '.fq']:
            # 未压缩文件也是允许的
            self.checks.append(ValidationCheck(
                check_type="compression_format",
                severity=ValidationSeverity.INFO,
                status="passed",
                message="文件未压缩（允许）"
            ))
        else:
            self.checks.append(ValidationCheck(
                check_type="compression_format",
                severity=ValidationSeverity.ERROR,
                status="failed",
                message=f"压缩格式不符合要求: {ext}，仅接受 .gz 或 .bz2",
                recommendation="请使用 gzip 或 bzip2 压缩文件"
            ))
    
    def _check_filename_format(self, file_path: str):
        """检查文件名规范"""
        filename = os.path.basename(file_path)
        # 移除扩展名中的句点（允许）
        name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
        
        has_forbidden = any(char in name_without_ext for char in self.FORBIDDEN_CHARS)
        
        if not has_forbidden:
            self.checks.append(ValidationCheck(
                check_type="filename_format",
                severity=ValidationSeverity.ERROR,
                status="passed",
                message=f"文件名符合规范: {filename}"
            ))
        else:
            forbidden_found = [char for char in self.FORBIDDEN_CHARS if char in name_without_ext]
            self.checks.append(ValidationCheck(
                check_type="filename_format",
                severity=ValidationSeverity.ERROR,
                status="failed",
                message=f"文件名包含禁止字符: {', '.join(forbidden_found)}",
                recommendation="请重命名文件，移除空格、连字符、括号等禁止字符"
            ))
    
    def _check_compression_integrity(self, file_path: str):
        """检查压缩文件完整性"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext == '.gz':
            # 尝试使用 gzip 命令测试
            import subprocess
            try:
                result = subprocess.run(
                    ['gzip', '-t', file_path],
                    capture_output=True,
                    timeout=30
                )
                if result.returncode == 0:
                    self.checks.append(ValidationCheck(
                        check_type="compression_integrity",
                        severity=ValidationSeverity.WARNING,
                        status="passed",
                        message="压缩文件完整性检查通过"
                    ))
                else:
                    self.checks.append(ValidationCheck(
                        check_type="compression_integrity",
                        severity=ValidationSeverity.ERROR,
                        status="failed",
                        message="压缩文件可能已损坏",
                        recommendation="请重新压缩文件"
                    ))
            except (FileNotFoundError, subprocess.TimeoutExpired):
                # gzip 命令不可用，跳过检查
                self.checks.append(ValidationCheck(
                    check_type="compression_integrity",
                    severity=ValidationSeverity.WARNING,
                    status="passed",
                    message="无法检查压缩完整性（gzip 命令不可用）"
                ))
        elif ext == '.bz2':
            import subprocess
            try:
                result = subprocess.run(
                    ['bzip2', '-t', file_path],
                    capture_output=True,
                    timeout=30
                )
                if result.returncode == 0:
                    self.checks.append(ValidationCheck(
                        check_type="compression_integrity",
                        severity=ValidationSeverity.WARNING,
                        status="passed",
                        message="压缩文件完整性检查通过"
                    ))
                else:
                    self.checks.append(ValidationCheck(
                        check_type="compression_integrity",
                        severity=ValidationSeverity.ERROR,
                        status="failed",
                        message="压缩文件可能已损坏",
                        recommendation="请重新压缩文件"
                    ))
            except (FileNotFoundError, subprocess.TimeoutExpired):
                self.checks.append(ValidationCheck(
                    check_type="compression_integrity",
                    severity=ValidationSeverity.WARNING,
                    status="passed",
                    message="无法检查压缩完整性（bzip2 命令不可用）"
                ))
        else:
            # 未压缩文件，跳过
            pass
    
    def _open_file(self, file_path: str):
        """根据压缩格式打开文件"""
        if file_path.endswith('.gz'):
            return gzip.open(file_path, 'rt', encoding='utf-8')
        elif file_path.endswith('.bz2'):
            return bz2.open(file_path, 'rt', encoding='utf-8')
        else:
            return open(file_path, 'r', encoding='utf-8')
    
    def _check_fastq_structure(self, file_path: str, max_reads: int = 1000):
        """检查FASTQ结构"""
        read_count = 0
        line_count = 0
        errors = []
        
        try:
            with self._open_file(file_path) as f:
                for line_num, line in enumerate(f, 1):
                    line = line.rstrip('\n\r')
                    line_count += 1
                    
                    # 每4行为一个读取
                    position_in_read = line_count % 4
                    
                    if position_in_read == 1:
                        # 应该是读取标识符行（@开头）
                        if not line.startswith('@'):
                            errors.append(f"第 {line_num} 行：读取标识符应以 @ 开头")
                        read_count += 1
                        if read_count >= max_reads:
                            break
                    elif position_in_read == 2:
                        # 碱基序列行（稍后检查）
                        pass
                    elif position_in_read == 3:
                        # 分隔符行（+开头）
                        if not line.startswith('+'):
                            errors.append(f"第 {line_num} 行：分隔符行应以 + 开头")
                    elif position_in_read == 0:
                        # 质量评分行（稍后检查长度）
                        pass
            
            if errors:
                self.checks.append(ValidationCheck(
                    check_type="fastq_structure",
                    severity=ValidationSeverity.ERROR,
                    status="failed",
                    message=f"FASTQ结构错误: {errors[0]}",
                    details={"errors": errors, "reads_checked": read_count}
                ))
            else:
                self.checks.append(ValidationCheck(
                    check_type="fastq_structure",
                    severity=ValidationSeverity.ERROR,
                    status="passed",
                    message=f"FASTQ结构正确: 检查了{read_count}个读取"
                ))
        except Exception as e:
            self.checks.append(ValidationCheck(
                check_type="fastq_structure",
                severity=ValidationSeverity.ERROR,
                status="failed",
                message=f"无法读取文件: {str(e)}"
            ))
    
    def _check_base_content(self, file_path: str, max_reads: int = 1000):
        """检查碱基序列格式"""
        read_count = 0
        line_count = 0
        errors = []
        
        try:
            with self._open_file(file_path) as f:
                for line_num, line in enumerate(f, 1):
                    line = line.rstrip('\n\r')
                    line_count += 1
                    
                    position_in_read = line_count % 4
                    
                    if position_in_read == 2:  # 碱基序列行
                        if not self.BASE_PATTERN.match(line):
                            invalid_chars = set(line) - set('ACGTNactgn.')
                            if invalid_chars:
                                errors.append(f"第 {line_num} 行：包含无效字符 {', '.join(invalid_chars)}")
                        read_count += 1
                        if read_count >= max_reads:
                            break
            
            if errors:
                self.checks.append(ValidationCheck(
                    check_type="base_content",
                    severity=ValidationSeverity.ERROR,
                    status="failed",
                    message=f"碱基序列格式错误: {errors[0]}",
                    details={"errors": errors}
                ))
            else:
                self.checks.append(ValidationCheck(
                    check_type="base_content",
                    severity=ValidationSeverity.ERROR,
                    status="passed",
                    message=f"碱基序列格式正确: 检查了{read_count}个读取"
                ))
        except Exception as e:
            self.checks.append(ValidationCheck(
                check_type="base_content",
                severity=ValidationSeverity.ERROR,
                status="failed",
                message=f"无法检查碱基序列: {str(e)}"
            ))
    
    def _check_quality_scores(self, file_path: str, max_reads: int = 1000):
        """检查质量评分格式"""
        read_count = 0
        line_count = 0
        errors = []
        phred_detected = None
        
        try:
            with self._open_file(file_path) as f:
                sequences = []
                qualities = []
                
                for line_num, line in enumerate(f, 1):
                    line = line.rstrip('\n\r')
                    line_count += 1
                    
                    position_in_read = line_count % 4
                    
                    if position_in_read == 2:  # 碱基序列行
                        sequences.append((line_num, line))
                    elif position_in_read == 0:  # 质量评分行
                        qualities.append((line_num, line))
                        
                        # 检查长度匹配
                        if sequences and qualities:
                            seq_line_num, seq = sequences[-1]
                            qual_line_num, qual = qualities[-1]
                            
                            if len(seq) != len(qual):
                                errors.append(f"第 {seq_line_num}/{qual_line_num} 行：序列长度({len(seq)})与质量评分长度({len(qual)})不匹配")
                            
                            # 检测 Phred 偏移量
                            if qual:
                                min_ascii = min(ord(c) for c in qual)
                                if phred_detected is None:
                                    if min_ascii >= 33 and min_ascii <= 126:
                                        phred_detected = 33
                                    elif min_ascii >= 64 and min_ascii <= 126:
                                        phred_detected = 64
                                
                                # 验证范围
                                if phred_detected == 33:
                                    if min_ascii < 33 or max(ord(c) for c in qual) > 126:
                                        errors.append(f"第 {qual_line_num} 行：质量评分超出 Phred 33 范围")
                                elif phred_detected == 64:
                                    if min_ascii < 64 or max(ord(c) for c in qual) > 126:
                                        errors.append(f"第 {qual_line_num} 行：质量评分超出 Phred 64 范围")
                        
                        read_count += 1
                        if read_count >= max_reads:
                            break
            
            if errors:
                self.checks.append(ValidationCheck(
                    check_type="quality_scores",
                    severity=ValidationSeverity.ERROR,
                    status="failed",
                    message=f"质量评分格式错误: {errors[0]}",
                    details={"errors": errors}
                ))
            else:
                phred_str = f"Phred {phred_detected}" if phred_detected else "未知"
                self.checks.append(ValidationCheck(
                    check_type="quality_scores",
                    severity=ValidationSeverity.ERROR,
                    status="passed",
                    message=f"质量评分格式正确 ({phred_str}): 检查了{read_count}个读取"
                ))
        except Exception as e:
            self.checks.append(ValidationCheck(
                check_type="quality_scores",
                severity=ValidationSeverity.ERROR,
                status="failed",
                message=f"无法检查质量评分: {str(e)}"
            ))
    
    def _check_casava_format(self, file_path: str, max_reads: int = 100):
        """检查 Illumina Casava 1.8+ 严格格式"""
        read_count = 0
        line_count = 0
        errors = []
        
        try:
            with self._open_file(file_path) as f:
                for line_num, line in enumerate(f, 1):
                    line = line.rstrip('\n\r')
                    line_count += 1
                    
                    position_in_read = line_count % 4
                    
                    if position_in_read == 1:  # 读取标识符行
                        if not self.ILLUMINA_CASAVA_PATTERN.match(line):
                            errors.append(f"第 {line_num} 行：不符合 Illumina Casava 1.8+ 格式")
                        read_count += 1
                        if read_count >= max_reads:
                            break
            
            if errors:
                self.checks.append(ValidationCheck(
                    check_type="casava_format",
                    severity=ValidationSeverity.ERROR,
                    status="failed",
                    message=f"Casava 格式检查失败: {errors[0]}",
                    details={"errors": errors}
                ))
            else:
                self.checks.append(ValidationCheck(
                    check_type="casava_format",
                    severity=ValidationSeverity.ERROR,
                    status="passed",
                    message=f"Casava 格式正确: 检查了{read_count}个读取"
                ))
        except Exception as e:
            self.checks.append(ValidationCheck(
                check_type="casava_format",
                severity=ValidationSeverity.ERROR,
                status="failed",
                message=f"无法检查 Casava 格式: {str(e)}"
            ))
    
    def get_errors(self) -> List[ValidationCheck]:
        """获取所有错误"""
        return [c for c in self.checks if c.severity == ValidationSeverity.ERROR and c.status == "failed"]
    
    def get_warnings(self) -> List[ValidationCheck]:
        """获取所有警告"""
        return [c for c in self.checks if c.severity == ValidationSeverity.WARNING and c.status == "failed"]






