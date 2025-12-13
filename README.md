# GSA FASTQ/BAM 数据校验工具

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS-lightgrey)](https://github.com)

**GSA FASTQ/BAM 数据校验工具** 是一个专门用于校验提交至 **GSA (Genome Sequence Archive, 组学原始数据归档库)** 的 FASTQ 和 BAM 文件格式和内容的工具，确保数据符合 GSA 官方提交要求。

---

## ✨ 核心特性

- 🔍 **全面校验** - 覆盖 GSA 所有格式要求（11 项核心检查）
- 📁 **多格式支持** - FASTQ (.fastq, .fq) 和 BAM (.bam) 格式
- 🔄 **双端数据校验** - 自动检测和验证配对文件（R1/R2）
- 📊 **详细报告** - JSON 和人类可读格式的校验报告
- 🔐 **MD5 校验** - 自动生成和验证 MD5 校验码
- ⚡ **批量处理** - 支持目录批量校验
- 🎯 **GSA 就绪** - 直接映射 GSA 官方条款编号

---

## 🚀 快速开始

### 安装

**无需安装依赖** - 本工具仅使用 Python 标准库！

```bash
# 克隆项目（替换为实际仓库地址）
git clone https://github.com/yourusername/gsa_fastq_validator.git
cd gsa_fastq_validator

# 直接使用（Python 3.6+）
python gsa_validator.py --help
```

**注意**：请将 `yourusername` 替换为实际的 GitHub 用户名或组织名。

### 基本使用

```bash
# 校验单个 FASTQ 文件
python gsa_validator.py sample.fastq.gz

# 校验 BAM 文件
python gsa_validator.py sample.bam

# 批量校验目录中的所有文件
python gsa_validator.py --batch /path/to/fastq/files

# 生成详细报告
python gsa_validator.py sample.fastq.gz --json-report report.json --verbose
```

---

## 📋 校验项目

### FASTQ 文件校验（11 项）

| # | 检查项 | GSA 条款 | 说明 |
|---|--------|---------|------|
| 1 | 文件存在性 | GSA-REQ-001 | 文件存在且可读 |
| 2 | 文件扩展名 | GSA-REQ-002 | `.fastq` 或 `.fq` |
| 3 | 压缩格式 | GSA-REQ-003 | 仅接受 `.gz` 或 `.bz2` |
| 4 | 文件名规范 | GSA-REQ-004 | 无禁止字符（空格、连字符等） |
| 5 | FASTQ 结构 | GSA-REQ-005 | 4 行/读取格式检查 |
| 6 | 碱基序列格式 | GSA-REQ-006 | 仅允许 ACGTNactgn. |
| 7 | 质量评分格式 | GSA-REQ-007 | Phred 33/64 自动检测 |
| 8 | 配对读取命名 | GSA-REQ-008 | 支持 `_1/_2` 或 `R1/R2` |
| 9 | Casava 格式 | GSA-REQ-009 | Illumina Casava 1.8+ 严格格式（可选） |
| 10 | 压缩完整性 | GSA-REQ-010 | 压缩文件完整性测试 |
| 11 | 双端数据匹配 | - | 读取数量、ID、顺序匹配 |

### BAM 文件校验

- ✅ 文件扩展名检查
- ✅ 文件命名规范
- ✅ 文件结构完整性（使用 samtools 或 pysam）
- ✅ 索引文件检查

---

## 💡 使用示例

### 示例 1：校验单个 FASTQ 文件

```bash
python gsa_validator.py sample.fastq.gz
```

**输出示例**：
```
======================================================================
文件: sample.fastq.gz
======================================================================

✓ sample.fastq.gz: 所有校验通过

✓ 通过的检查:
  - [file_existence] ✓ 文件存在且可读
  - [file_extension] ✓ 文件扩展名正确: .fastq.gz
  - [compression_format] ✓ 压缩格式正确: .gz
  - [filename_format] ✓ 文件名符合规范
  - [fastq_structure] ✓ FASTQ结构正确: 检查了1000个读取
  - [base_content] ✓ 碱基序列格式正确
  - [quality_scores] ✓ 质量评分格式正确 (Phred 33)
======================================================================
```

### 示例 2：校验双端数据

```bash
# 分别校验两个配对文件
python gsa_validator.py sample_R1.fastq.gz
python gsa_validator.py sample_R2.fastq.gz

# 批量校验目录中的所有配对文件
python gsa_validator.py --batch /path/to/paired/files --verbose
```

**注意**：完整的配对文件匹配验证（读取数量、ID 匹配等）需要使用专门的验证脚本，详见 `example/README.md`。

**配对文件验证输出**：
```
======================================================================
验证配对 FASTQ 文件
======================================================================
文件1 (R1): sample_R1.fastq.gz
文件2 (R2): sample_R2.fastq.gz

📊 统计读取数量...
  文件1读取数: 88,118
  文件2读取数: 88,118
  ✓ 读取数量匹配

🔍 检查读取ID匹配（检查前 1000 个读取）...
  ✓ 所有检查的读取ID都匹配

📦 文件大小:
  文件1: 2.73 MB
  文件2: 3.16 MB
  大小比例: 1.16x
  ✓ 文件大小比例合理

======================================================================
✓ 配对文件验证通过！
======================================================================
```

### 示例 3：生成 MD5 校验码

```bash
# 生成 MD5 校验码文件
python gsa_validator.py sample.fastq.gz --generate-md5

# 验证 MD5 校验码
python gsa_validator.py sample.fastq.gz --verify-md5 --md5-file sample.fastq.gz.md5
```

### 示例 4：批量校验并生成报告

```bash
# 批量校验目录中的所有 FASTQ 文件
python gsa_validator.py --batch /path/to/fastq/files \
  --json-report batch_report.json \
  --verbose
```

### 示例 5：严格模式（检查 Casava 格式）

```bash
# 启用 Illumina Casava 1.8+ 严格格式检查
python gsa_validator.py sample_R1.fastq.gz --check-casava --verbose
```

### 示例 6：使用示例脚本

运行提供的示例脚本查看各种用法：

```bash
python example_usage.py
```

---

## 🔧 命令行选项

```bash
usage: gsa_validator.py [-h] [--batch DIR] [--pattern PATTERN]
                         [--generate-md5] [--verify-md5] [--md5-file MD5_FILE]
                         [--json-report JSON_REPORT] [--check-casava]
                         [--verbose]
                         [file]

GSA FASTQ/BAM 数据校验工具

positional arguments:
  file                  要校验的 FASTQ 或 BAM 文件路径

optional arguments:
  -h, --help            显示帮助信息
  --batch DIR, -b DIR   批量校验目录中的所有文件
  --pattern PATTERN, -p PATTERN
                        批量校验时的文件匹配模式（默认: *.fastq*）
  --generate-md5, -g    生成 MD5 校验码文件
  --verify-md5, -v      验证 MD5 校验码
  --md5-file MD5_FILE, -m MD5_FILE
                        MD5 校验码文件路径（用于验证）
  --json-report JSON_REPORT, -j JSON_REPORT
                        生成 JSON 格式的详细报告
  --check-casava        检查 Illumina Casava 1.8+ 严格格式（双端数据）
  --verbose             详细输出模式
```

---

## 📖 Python API

### 基本使用

**方式1：作为包导入（推荐）**

```python
from gsa_fastq_validator import GSAFastQValidator, ValidationReport

# 创建校验器
validator = GSAFastQValidator()

# 校验文件
report = validator.validate("sample.fastq.gz")

# 检查结果
if report.is_valid:
    print("✓ 校验通过")
else:
    errors = report.get_errors()
    for error in errors:
        print(f"❌ {error.check_type}: {error.message}")
```

**方式2：直接导入模块（脚本中使用）**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from validator import GSAFastQValidator, ValidationReport

# 使用方式相同
validator = GSAFastQValidator()
report = validator.validate("sample.fastq.gz")
```

### 校验 BAM 文件

```python
from gsa_fastq_validator import GSABAMValidator

# 创建 BAM 校验器
validator = GSABAMValidator()

# 校验 BAM 文件
report = validator.validate("sample.bam")

if report.is_valid:
    print("✓ BAM 文件校验通过")
```

### 生成 MD5 校验码

```python
from gsa_fastq_validator import MD5Checker

# 计算 MD5
md5_value = MD5Checker.calculate_md5("sample.fastq.gz")
print(f"MD5: {md5_value}")

# 生成 MD5 文件
md5_file = MD5Checker.generate_md5_file("sample.fastq.gz")

# 验证 MD5
success, message = MD5Checker.verify_md5(
    "sample.fastq.gz", 
    md5_file_path="sample.fastq.gz.md5"
)
print(message)
```

### 验证双端数据

```python
from gsa_fastq_validator import GSAFastQValidator

# 分别校验两个配对文件
validator = GSAFastQValidator()

# 校验 R1 文件
report1 = validator.validate("sample_R1.fastq.gz")

# 校验 R2 文件
report2 = validator.validate("sample_R2.fastq.gz")

# 检查两个文件是否都通过校验
if report1.is_valid and report2.is_valid:
    print("✓ 配对文件验证通过")
    
    # 可以进一步检查读取数量是否匹配
    # （需要手动读取文件统计，或使用外部工具）
else:
    print("✗ 配对文件验证失败")
    if not report1.is_valid:
        print("R1 文件错误:")
        for error in report1.get_errors():
            print(f"  - {error.message}")
    if not report2.is_valid:
        print("R2 文件错误:")
        for error in report2.get_errors():
            print(f"  - {error.message}")
```

**注意**：完整的配对文件匹配验证（读取数量、ID 匹配等）需要使用专门的工具脚本，详见 `example/README.md`。

### 生成 GSA 就绪报告

```python
from gsa_fastq_validator import GSAFastQValidator, GSAReportGenerator

# 校验文件
validator = GSAFastQValidator()
report = validator.validate("sample.fastq.gz")

# 生成 JSON 报告
json_data = GSAReportGenerator.generate_json_report(report, "report.json")

# 生成人类可读报告
text_report = GSAReportGenerator.generate_human_readable_report(report)
print(text_report)
```

---

## 📊 GSA 提交要求参考

### 文件格式要求

| 要求 | 说明 |
|------|------|
| **扩展名** | `.fastq` 或 `.fq` |
| **压缩格式** | 仅接受 gzip (`.gz`) 或 bzip2 (`.bz2`) |
| **不接受** | 7-Zip、RAR、TAR 等格式 |

### FASTQ 格式要求

- **结构**：每个读取必须包含 4 行
  1. 读取标识符行（以 `@` 开头）
  2. 碱基序列行
  3. 分隔符行（以 `+` 开头）
  4. 质量评分行（与序列行长度相同）

- **碱基序列**：仅允许字符 `A`, `C`, `G`, `T`, `N`（未知碱基），支持小写和点号 `.`

- **质量评分**：必须使用 Phred 评分，支持 ASCII 编码（Phred 33 或 64）

### 文件命名要求

- 文件名必须唯一
- **禁止字符**：空格、连字符、括号、正反斜杠
- **注意**：文件扩展名中的句点（如 `.fastq.gz`）是允许的，但文件名主体中应避免使用句点
- **配对读取**：使用 `_1`/`_2` 或 `R1`/`R2` 后缀

### 双端数据要求

- **配对文件数量**：双端测序应提供 2 个文件（R1 和 R2）
- **读取数量**：两个文件应包含相同数量的读取
- **读取 ID 匹配**：对应位置的读取 ID 应匹配（去除配对标识后）
- **文件命名**：配对文件应使用一致的命名模式
- **读取顺序**：读取应按相同顺序排列
- **文件大小**：两个文件大小应相近（比例不应超过 2 倍）

### MD5 校验码要求

- 每个文件需要提供 MD5 校验码
- 格式：`md5_value  filename`

---

## 🛠️ 依赖要求

### 必需依赖

**无外部依赖** - 本工具仅使用 Python 标准库！

### 可选依赖（用于高级功能）

```bash
# BAM 文件校验（二选一）
samtools  # 推荐：使用系统命令
# 或
pip install pysam  # Python 库

# 压缩文件完整性检查（系统命令，通常已安装）
gzip   # 用于 .gz 文件
bzip2  # 用于 .bz2 文件
```

---

## 📁 项目结构

```
gsa_fastq_validator/
├── README.md                  # 本文件
├── requirements.txt           # Python 依赖（可选）
├── __init__.py               # 包初始化文件
│
├── validator.py              # FASTQ 验证器核心
├── bam_validator.py          # BAM 文件验证器
├── gsa_validator.py          # 命令行工具
├── md5_checker.py           # MD5 校验工具
├── report_generator.py      # 报告生成器
├── example_usage.py          # 使用示例脚本
│
└── example/                  # 示例和测试文件
    ├── README.md             # 示例文件说明
    ├── extract_small_bam.py  # BAM 文件提取工具
    ├── sample_*.fastq.gz     # 标准测试数据
    ├── error_*.fastq.gz      # 错误测试数据
    ├── ERR10064847_*.fastq.gz # 真实测试数据（从 ENA 下载）
    └── *.bam                 # BAM 测试文件
```

---

## ❓ 常见问题

### Q1: 工具需要安装哪些依赖？

**A:** 基本功能无需任何外部依赖，仅使用 Python 标准库。BAM 文件校验需要安装 `samtools` 或 `pysam`（可选）。

### Q2: 如何验证双端数据？

**A:** 有两种方法：
1. 分别校验两个文件：`python gsa_validator.py file_R1.fastq.gz` 和 `python gsa_validator.py file_R2.fastq.gz`
2. 批量校验目录：`python gsa_validator.py --batch /path/to/files`，工具会自动检测配对关系
3. 详细的配对文件匹配验证（读取数量、ID 匹配等）请参考 `example/README.md` 中的说明

### Q3: MD5 校验码文件格式是什么？

**A:** 标准格式：`md5_value  filename`（MD5 值和文件名之间用两个空格分隔）

### Q4: 支持哪些压缩格式？

**A:** GSA 仅接受 `.gz`（gzip）和 `.bz2`（bzip2）格式，不支持其他压缩格式。

### Q5: 如何生成 GSA 提交报告？

**A:** 使用 `--json-report` 选项生成详细的 JSON 报告，报告中包含所有 GSA 条款编号映射。

### Q6: Casava 格式检查是什么？

**A:** Illumina Casava 1.8+ 格式是双端数据的严格命名规范。使用 `--check-casava` 选项启用检查。格式要求读取标识符符合：`@instrument:run_id:flowcell_id:lane:tile:x:y read:filtered:control:index`

### Q7: 如何查看使用示例？

**A:** 运行 `python example_usage.py` 查看各种使用示例，或查看 `example/README.md` 了解测试文件的使用方法。

---

## 📚 参考文档

- **GSA 官方提交指南**: https://ngdc.cncb.ac.cn/gsa/document/GSA-GSA_Submission_Guide_2.3.cn.pdf
- **GSA 标准页面**: https://ngdc.cncb.ac.cn/gsa/support/standardsGsa
- **联系方式**: gsa@big.ac.cn

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献方式

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📜 许可证

本工具遵循 **MIT 许可证**。

---

## 📈 版本历史

### v1.1.0 (2025-01-XX)
- ✅ 新增 BAM 文件校验支持
- ✅ 新增双端数据校验功能
- ✅ 支持配对文件匹配验证（读取数量、ID 匹配、文件大小）
- ✅ 新增 Casava 格式严格检查
- ✅ 新增压缩文件完整性检查
- ✅ 新增 GSA 就绪报告生成（JSON + 文本）
- ✅ 增强 Phred 分数和双端文件检查

### v1.0.0 (2025-01-XX)
- ✅ 初始版本
- ✅ 实现 GSA FASTQ 文件格式校验
- ✅ 实现 MD5 校验码生成和验证
- ✅ 支持批量校验

---

## 👥 作者

GSA Validation Tool Team

---

## 🙏 致谢

感谢以下项目的支持：

- [GSA (Genome Sequence Archive)](https://ngdc.cncb.ac.cn/gsa/) - 组学原始数据归档库
- [SAMtools](http://www.htslib.org/) - BAM 文件处理工具
- [PySAM](https://github.com/pysam-developers/pysam) - Python BAM 文件处理库

---

**Made with ❤️ for GSA data submission**
