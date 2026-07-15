# Manufacturing AI Assistant

[English](#english) | [中文](#中文) | [한국어](#한국어)

---

<a name="english"></a>
# English

An AI-powered manufacturing intelligence platform for production monitoring, natural-language data analysis, equipment health evaluation, root-cause investigation, and document-based knowledge retrieval.

The project combines structured manufacturing data with large language models to support secure Text-to-SQL, RAG, hybrid analysis, automatic visualization, and explainable manufacturing insights.

## Overview

Manufacturing AI Assistant is designed as a portfolio-grade industrial AI application.

It enables users to:

- Monitor production and quality KPIs
- Query manufacturing data using natural language
- Generate safe SQL automatically
- Analyze abnormal equipment and product patterns
- Search equipment manuals and SOP documents
- Combine database evidence with document guidance
- Evaluate equipment health using explainable rules
- Perform evidence-based root-cause analysis

## System Architecture

```
User Question
      |
      v
Intent Router
      |
      +-- Database
      |      |
      |      v
      |  Text-to-SQL
      |      |
      |      v
      |  SQL Validator
      |      |
      |      v
      |  Manufacturing Database
      |      |
      |      v
      |  Analysis + Visualization
      |
      +-- Knowledge
      |      |
      |      v
      |  Semantic Retrieval
      |      |
      |      v
      |  SOP / Manual Context
      |      |
      |      v
      |  Grounded Answer
      |
      +-- Hybrid
             |
             v
      Query Decomposition
             |
             +-- Database Question
             +-- Knowledge Question
             |
             v
      Integrated Manufacturing Analysis
```

## Core Features

### Manufacturing Dashboard
- Production order monitoring
- Production quantity tracking
- Weight measurement analysis
- Abnormal rate monitoring
- Rework quantity and rate
- Product and equipment comparison
- Recent abnormal measurement records

### Equipment Health
- Equipment health score from 0 to 100
- Abnormal-rate penalty
- Rework-rate penalty
- Recent trend penalty
- Weight-deviation penalty
- Health status classification
- Equipment-level detail view

### Root Cause Analysis
- Automatically selects high-risk equipment
- Separates OVER and UNDER anomalies
- Identifies top contributing products
- Analyzes daily and hourly anomaly patterns
- Compares recent periods
- Retrieves relevant SOP guidance
- Distinguishes observed facts from possible causes

### AI Assistant
- Natural-language manufacturing questions
- Secure Text-to-SQL
- SQL validation and table whitelist
- Automatic chart generation
- AI analysis of query results
- Intent routing (database / knowledge / hybrid / general)
- Hybrid SQL and RAG analysis
- Query decomposition
- Chat history during the active session

### Knowledge Search
- Equipment manual retrieval
- SOP retrieval
- Alarm-code search
- Calibration-procedure search
- Product-changeover guidance
- Source references and similarity scores
- Multilingual semantic retrieval

### System Settings
- Application status
- Database connection status
- LLM configuration
- Knowledge-index status
- Database statistics
- Document and chunk counts

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit ≥ 1.45 |
| Database | SQLite |
| LLM | DeepSeek (OpenAI-compatible) |
| Embeddings | sentence-transformers (multilingual) |
| Vector Search | FAISS |
| Visualization | Plotly |
| SQL Safety | sqlglot |
| Data | Pandas, NumPy |
| Runtime | Python 3.11 (conda) |

## Project Structure

```
manufacturing-ai-assistant/
├── app/
│   ├── database/
│   │   └── connection.py
│   ├── services/              # 14 service modules
│   └── tools/
│       ├── schema_tool.py
│       ├── sql_validator.py
│       ├── document_loader.py
│       └── text_splitter.py
│
├── frontend/
│   ├── Home.py
│   ├── components/
│   │   ├── charts.py
│   │   ├── filters.py
│   │   ├── header.py
│   │   ├── metrics.py
│   │   ├── styles.py
│   │   └── tables.py
│   └── pages/
│       ├── 1_Dashboard.py
│       ├── 2_Equipment_Health.py
│       ├── 3_Root_Cause.py
│       ├── 4_AI_Assistant.py
│       ├── 5_Knowledge.py
│       └── 6_Settings.py
│
├── data/
│   ├── raw/
│   ├── knowledge/
│   └── manufacturing.db
│
├── docs/
│   ├── equipment_manual.md
│   └── quality_sop.md
│
├── scripts/
├── evaluation/
├── tests/
├── setup.ps1              # One-command environment setup (Windows/conda)
├── run.ps1                # One-command app launch (Windows/conda)
├── requirements.txt
├── .env.example
└── README.md
```

## Quick Start

### Option A — Automated Setup (Windows + conda)

```powershell
# First-time setup: creates conda env, installs deps, generates data, builds index
.\setup.ps1

# Launch the app every time after setup
.\run.ps1
```

### Option B — Manual Setup

```bash
# 1. Create and activate conda environment (Python 3.11)
conda create -n manufacturing-ai python=3.11 -y
conda activate manufacturing-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env: set DEEPSEEK_API_KEY and adjust settings as needed

# 4. Generate synthetic data and initialize database
python scripts/generate_data.py
python scripts/init_database.py

# 5. Build knowledge index
python scripts/build_knowledge_index.py

# 6. Launch the application
streamlit run frontend/Home.py
```

The app runs on http://localhost:8501 by default.

## Environment Configuration

Key settings in `.env` (see `.env.example` for the full template):

| Variable | Description | Default |
|----------|-------------|---------|
| `DEEPSEEK_API_KEY` | LLM API key | — |
| `DEEPSEEK_BASE_URL` | API base URL | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | Model name | `deepseek-chat` |
| `LLM_TEMPERATURE` | Generation temperature | `0.0` |
| `DATABASE_PATH` | SQLite file path | `data/manufacturing.db` |
| `EMBEDDING_MODEL` | Sentence-transformer model | `paraphrase-multilingual-MiniLM-L12-v2` |
| `TOP_K` | RAG top-k chunks | `5` |
| `SIMILARITY_THRESHOLD` | Minimum cosine similarity | `0.35` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

---

<a name="中文"></a>
# 中文

基于 AI 的制造业智能平台，提供生产监控、自然语言数据分析、设备健康评估、根因调查和文档知识检索功能。

本项目将结构化制造数据与大型语言模型相结合，支持安全的 Text-to-SQL、RAG、混合分析、自动可视化，以及可解释的制造业洞察。

## 项目简介

Manufacturing AI Assistant 是一个面向工业场景的作品集级 AI 应用。

主要功能：

- 监控生产与质量 KPI
- 用自然语言查询制造数据
- 自动生成安全的 SQL 语句
- 分析设备和产品的异常模式
- 搜索设备手册和 SOP 文档
- 将数据库证据与文档指导相结合
- 使用可解释规则评估设备健康状态
- 开展基于证据的根因分析

## 系统架构

```
用户提问
    |
    v
意图路由器
    |
    +-- 数据库
    |      |
    |      v
    |  Text-to-SQL
    |      |
    |      v
    |  SQL 校验器
    |      |
    |      v
    |  制造数据库
    |      |
    |      v
    |  分析 + 可视化
    |
    +-- 知识库
    |      |
    |      v
    |  语义检索
    |      |
    |      v
    |  SOP / 手册上下文
    |      |
    |      v
    |  有据可查的回答
    |
    +-- 混合模式
           |
           v
    查询分解
           |
           +-- 数据库子问题
           +-- 知识库子问题
           |
           v
    综合制造业分析
```

## 核心功能

### 制造业看板
- 生产工单监控
- 生产数量追踪
- 重量测量分析
- 异常率监控
- 返工数量与返工率
- 产品与设备对比
- 近期异常测量记录

### 设备健康
- 设备健康评分（0–100 分）
- 异常率扣分项
- 返工率扣分项
- 近期趋势扣分项
- 重量偏差扣分项
- 健康状态分级
- 设备级别详情视图

### 根因分析
- 自动筛选高风险设备
- 分离 OVER 和 UNDER 异常
- 识别贡献最大的产品
- 分析每日与每小时异常模式
- 对比近期时间段
- 检索相关 SOP 指导
- 区分观察事实与可能原因

### AI 助手
- 制造业自然语言提问
- 安全 Text-to-SQL
- SQL 校验与表名白名单
- 自动生成图表
- AI 对查询结果进行分析
- 意图路由（数据库 / 知识库 / 混合 / 通用）
- SQL 与 RAG 混合分析
- 查询分解
- 当前会话的聊天历史

### 知识搜索
- 设备手册检索
- SOP 检索
- 报警码搜索
- 校准程序搜索
- 换产指导
- 来源引用与相似度评分
- 多语言语义检索

### 系统设置
- 应用状态
- 数据库连接状态
- LLM 配置
- 知识库索引状态
- 数据库统计信息
- 文档与 Chunk 数量

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Streamlit ≥ 1.45 |
| 数据库 | SQLite |
| LLM | DeepSeek（兼容 OpenAI API） |
| 嵌入模型 | sentence-transformers（多语言） |
| 向量检索 | FAISS |
| 可视化 | Plotly |
| SQL 安全 | sqlglot |
| 数据处理 | Pandas、NumPy |
| 运行环境 | Python 3.11（conda） |

## 项目结构

```
manufacturing-ai-assistant/
├── app/
│   ├── database/
│   │   └── connection.py
│   ├── services/              # 14 个服务模块
│   └── tools/
│       ├── schema_tool.py
│       ├── sql_validator.py
│       ├── document_loader.py
│       └── text_splitter.py
│
├── frontend/
│   ├── Home.py
│   ├── components/
│   └── pages/
│       ├── 1_Dashboard.py
│       ├── 2_Equipment_Health.py
│       ├── 3_Root_Cause.py
│       ├── 4_AI_Assistant.py
│       ├── 5_Knowledge.py
│       └── 6_Settings.py
│
├── data/
│   ├── raw/
│   ├── knowledge/
│   └── manufacturing.db
│
├── docs/
│   ├── equipment_manual.md
│   └── quality_sop.md
│
├── scripts/
├── evaluation/
├── tests/
├── setup.ps1              # 一键环境初始化（Windows/conda）
├── run.ps1                # 一键启动应用（Windows/conda）
├── requirements.txt
├── .env.example
└── README.md
```

## 快速开始

### 方式 A — 自动化安装（Windows + conda）

```powershell
# 首次安装：自动创建 conda 环境、安装依赖、生成数据、构建索引
.\setup.ps1

# 之后每次启动应用
.\run.ps1
```

### 方式 B — 手动安装

```bash
# 1. 创建并激活 conda 环境（Python 3.11）
conda create -n manufacturing-ai python=3.11 -y
conda activate manufacturing-ai

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填写 DEEPSEEK_API_KEY 及其他配置

# 4. 生成模拟数据并初始化数据库
python scripts/generate_data.py
python scripts/init_database.py

# 5. 构建知识库索引
python scripts/build_knowledge_index.py

# 6. 启动应用
streamlit run frontend/Home.py
```

应用默认运行在 http://localhost:8501。

## 环境变量配置

`.env` 中的关键配置项（完整模板见 `.env.example`）：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | LLM API 密钥 | — |
| `DEEPSEEK_BASE_URL` | API 基础 URL | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | 模型名称 | `deepseek-chat` |
| `LLM_TEMPERATURE` | 生成温度 | `0.0` |
| `DATABASE_PATH` | SQLite 文件路径 | `data/manufacturing.db` |
| `EMBEDDING_MODEL` | 句向量模型 | `paraphrase-multilingual-MiniLM-L12-v2` |
| `TOP_K` | RAG 检索的 Chunk 数量 | `5` |
| `SIMILARITY_THRESHOLD` | 最低余弦相似度 | `0.35` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

---

<a name="한국어"></a>
# 한국어

생산 모니터링, 자연어 데이터 분석, 설비 건강 평가, 근본 원인 조사, 문서 기반 지식 검색을 위한 AI 기반 제조 인텔리전스 플랫폼입니다.

이 프로젝트는 구조화된 제조 데이터와 대형 언어 모델을 결합하여 안전한 Text-to-SQL, RAG, 하이브리드 분석, 자동 시각화, 그리고 설명 가능한 제조 인사이트를 제공합니다.

## 프로젝트 개요

Manufacturing AI Assistant는 포트폴리오 수준의 산업용 AI 애플리케이션입니다.

주요 기능:

- 생산 및 품질 KPI 모니터링
- 자연어로 제조 데이터 조회
- 안전한 SQL 자동 생성
- 설비 및 제품의 이상 패턴 분석
- 설비 매뉴얼 및 SOP 문서 검색
- 데이터베이스 근거와 문서 지침의 통합
- 설명 가능한 규칙 기반 설비 건강 평가
- 근거 기반 근본 원인 분석

## 시스템 아키텍처

```
사용자 질문
    |
    v
인텐트 라우터
    |
    +-- 데이터베이스
    |      |
    |      v
    |  Text-to-SQL
    |      |
    |      v
    |  SQL 검증기
    |      |
    |      v
    |  제조 데이터베이스
    |      |
    |      v
    |  분석 + 시각화
    |
    +-- 지식베이스
    |      |
    |      v
    |  시맨틱 검색
    |      |
    |      v
    |  SOP / 매뉴얼 컨텍스트
    |      |
    |      v
    |  근거 기반 답변
    |
    +-- 하이브리드
           |
           v
    쿼리 분해
           |
           +-- 데이터베이스 서브 질문
           +-- 지식베이스 서브 질문
           |
           v
    통합 제조 분석
```

## 핵심 기능

### 제조 대시보드
- 생산 작업 지시 모니터링
- 생산 수량 추적
- 중량 측정 분석
- 이상률 모니터링
- 재작업 수량 및 비율
- 제품 및 설비 비교
- 최근 이상 측정 기록

### 설비 건강 평가
- 설비 건강 점수 (0–100점)
- 이상률 감점 항목
- 재작업률 감점 항목
- 최근 추세 감점 항목
- 중량 편차 감점 항목
- 건강 상태 등급 분류
- 설비별 상세 보기

### 근본 원인 분석
- 고위험 설비 자동 선별
- OVER / UNDER 이상 유형 분리
- 주요 기여 제품 식별
- 일별 및 시간별 이상 패턴 분석
- 최근 기간 비교
- 관련 SOP 지침 검색
- 관찰 사실과 가능한 원인 구분

### AI 어시스턴트
- 제조 분야 자연어 질문
- 안전한 Text-to-SQL
- SQL 검증 및 테이블 화이트리스트
- 자동 차트 생성
- 쿼리 결과 AI 분석
- 인텐트 라우팅 (데이터베이스 / 지식베이스 / 하이브리드 / 일반)
- SQL + RAG 하이브리드 분석
- 쿼리 분해
- 현재 세션 채팅 히스토리

### 지식 검색
- 설비 매뉴얼 검색
- SOP 검색
- 알람 코드 검색
- 교정 절차 검색
- 제품 교체 지침
- 출처 참조 및 유사도 점수
- 다국어 시맨틱 검색

### 시스템 설정
- 애플리케이션 상태
- 데이터베이스 연결 상태
- LLM 구성
- 지식베이스 인덱스 상태
- 데이터베이스 통계
- 문서 및 청크 수

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| 프론트엔드 | Streamlit ≥ 1.45 |
| 데이터베이스 | SQLite |
| LLM | DeepSeek (OpenAI 호환) |
| 임베딩 | sentence-transformers (다국어) |
| 벡터 검색 | FAISS |
| 시각화 | Plotly |
| SQL 안전성 | sqlglot |
| 데이터 처리 | Pandas, NumPy |
| 런타임 | Python 3.11 (conda) |

## 프로젝트 구조

```
manufacturing-ai-assistant/
├── app/
│   ├── database/
│   │   └── connection.py
│   ├── services/              # 14개 서비스 모듈
│   └── tools/
│       ├── schema_tool.py
│       ├── sql_validator.py
│       ├── document_loader.py
│       └── text_splitter.py
│
├── frontend/
│   ├── Home.py
│   ├── components/
│   └── pages/
│       ├── 1_Dashboard.py
│       ├── 2_Equipment_Health.py
│       ├── 3_Root_Cause.py
│       ├── 4_AI_Assistant.py
│       ├── 5_Knowledge.py
│       └── 6_Settings.py
│
├── data/
│   ├── raw/
│   ├── knowledge/
│   └── manufacturing.db
│
├── docs/
│   ├── equipment_manual.md
│   └── quality_sop.md
│
├── scripts/
├── evaluation/
├── tests/
├── setup.ps1              # 원클릭 환경 설정 (Windows/conda)
├── run.ps1                # 원클릭 앱 실행 (Windows/conda)
├── requirements.txt
├── .env.example
└── README.md
```

## 빠른 시작

### 방법 A — 자동 설정 (Windows + conda)

```powershell
# 최초 설정: conda 환경 생성, 의존성 설치, 데이터 생성, 인덱스 구축 자동 실행
.\setup.ps1

# 이후 앱 실행 시
.\run.ps1
```

### 방법 B — 수동 설정

```bash
# 1. conda 환경 생성 및 활성화 (Python 3.11)
conda create -n manufacturing-ai python=3.11 -y
conda activate manufacturing-ai

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일 편집: DEEPSEEK_API_KEY 및 기타 설정 입력

# 4. 합성 데이터 생성 및 데이터베이스 초기화
python scripts/generate_data.py
python scripts/init_database.py

# 5. 지식베이스 인덱스 구축
python scripts/build_knowledge_index.py

# 6. 애플리케이션 실행
streamlit run frontend/Home.py
```

앱은 기본적으로 http://localhost:8501 에서 실행됩니다.

## 환경 변수 설정

`.env`의 주요 설정 항목 (전체 템플릿은 `.env.example` 참조):

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | LLM API 키 | — |
| `DEEPSEEK_BASE_URL` | API 기본 URL | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | 모델 이름 | `deepseek-chat` |
| `LLM_TEMPERATURE` | 생성 온도 | `0.0` |
| `DATABASE_PATH` | SQLite 파일 경로 | `data/manufacturing.db` |
| `EMBEDDING_MODEL` | 문장 임베딩 모델 | `paraphrase-multilingual-MiniLM-L12-v2` |
| `TOP_K` | RAG 검색 청크 수 | `5` |
| `SIMILARITY_THRESHOLD` | 최소 코사인 유사도 | `0.35` |
| `LOG_LEVEL` | 로그 레벨 | `INFO` |
