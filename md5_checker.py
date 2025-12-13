#!/usr/bin/env python3
"""
MD5校验码工具

用于生成和验证FASTQ/BAM文件的MD5校验码。
"""

import hashlib
import os
from pathlib import Path
from typing import Tuple, Optional

# 无外部依赖


class MD5Checker:
    """MD5校验码工具类"""
    
    @staticmethod
    def calculate_md5(file_path: str, chunk_size: int = 8192) -> str:
        """
        计算文件的MD5校验码
        
        Args:
            file_path: 文件路径
            chunk_size: 读取块大小（字节）
            
        Returns:
            MD5校验码（32位十六进制字符串）
        """
        md5_hash = hashlib.md5()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                md5_hash.update(chunk)
        
        return md5_hash.hexdigest()
    
    @staticmethod
    def generate_md5_file(file_path: str, output_path: Optional[str] = None) -> str:
        """
        生成MD5校验码文件
        
        Args:
            file_path: 要计算MD5的文件路径
            output_path: 输出MD5文件路径（默认：原文件路径 + .md5）
            
        Returns:
            MD5文件路径
        """
        if output_path is None:
            output_path = file_path + '.md5'
        
        md5_value = MD5Checker.calculate_md5(file_path)
        filename = os.path.basename(file_path)
        
        # GSA标准格式：md5_value  filename（两个空格）
        with open(output_path, 'w') as f:
            f.write(f"{md5_value}  {filename}\n")
        
        return output_path
    
    @staticmethod
    def verify_md5(file_path: str, md5_file_path: Optional[str] = None, md5_value: Optional[str] = None) -> Tuple[bool, str]:
        """
        验证文件的MD5校验码
        
        Args:
            file_path: 要验证的文件路径
            md5_file_path: MD5文件路径（如果提供，会从中读取MD5值）
            md5_value: 直接提供的MD5值（如果提供，优先使用）
            
        Returns:
            (是否匹配, 消息)
        """
        if md5_value is None:
            if md5_file_path is None:
                # 自动查找同名.md5文件
                md5_file_path = file_path + '.md5'
            
            if not os.path.exists(md5_file_path):
                return False, f"MD5文件不存在: {md5_file_path}"
            
            # 从MD5文件中读取
            with open(md5_file_path, 'r') as f:
                line = f.readline().strip()
                # 解析格式：md5_value  filename
                parts = line.split('  ', 1)  # 两个空格分隔
                if len(parts) >= 1:
                    md5_value = parts[0].strip()
                else:
                    return False, f"MD5文件格式错误: {md5_file_path}"
        
        # 计算文件的MD5
        calculated_md5 = MD5Checker.calculate_md5(file_path)
        
        if calculated_md5.lower() == md5_value.lower():
            return True, f"✓ MD5校验通过: {calculated_md5}"
        else:
            return False, f"✗ MD5校验失败: 期望 {md5_value}, 实际 {calculated_md5}"
    
    @staticmethod
    def read_md5_from_file(md5_file_path: str) -> Tuple[str, str]:
        """
        从MD5文件中读取MD5值和文件名
        
        Args:
            md5_file_path: MD5文件路径
            
        Returns:
            (MD5值, 文件名)
        """
        with open(md5_file_path, 'r') as f:
            line = f.readline().strip()
            parts = line.split('  ', 1)  # 两个空格分隔
            md5_value = parts[0].strip()
            filename = parts[1].strip() if len(parts) > 1 else ""
            return md5_value, filename

