# 全栈开发项目规则
## 核心分工规则（强制执行）
所有开发任务必须按照以下分工分配给对应的智能体，禁止主智能体亲自编写代码：
1.  UI Designer (/ui-designer)**
    - 负责所有界面设计、视觉规范、组件样式和响应式布局
    - 任何涉及页面外观、颜色、排版、交互的任务必须先调用此智能体
    - 输出设计稿和组件规范后，再交给前端架构师实现

2.  Frontend Architect (/frontend-architect)**
    - 负责所有前端代码的编写：页面、组件、路由、状态管理、API调用
    - 必须严格遵循UI Designer输出的设计规范
    - 负责前端性能优化和代码质量

3.  Backend Architect (/backend-architect)**
    - 负责所有后端代码的编写：API接口、业务逻辑、数据库操作、权限系统
    - 负责数据库Schema设计和ORM配置
    - 输出API文档后，再交给前端架构师对接

4.  API Test Pro (/api-test-pro)**
    - 每个后端接口开发完成后，必须自动调用此智能体编写单元测试和集成测试
    - 测试必须覆盖正常流程、边界条件和异常情况
    - 测试不通过的接口必须修复后才能继续开发

5.  Performance Expert (/performance-expert)**
    - 每个功能模块开发完成后，自动调用此智能体进行性能分析
    - 识别并修复前端加载速度、后端响应时间和数据库查询性能问题
    - 输出性能优化报告和改进建议

6.  AI Integration Eng (/ai-integration-engineer)**
    - 负责所有AI相关功能的开发：大模型调用、向量数据库、RAG系统等
    - 负责API密钥管理和安全配置
    - 优化AI响应速度和成本

7.  DevOps Architect (/devops-architect)**
    - 负责项目的打包构建、环境配置和部署上线
    - 编写Dockerfile和docker-compose.yml
    - 配置CI/CD流水线和环境变量

8.  Compliance Checker (/compliance-checker)**
    - 所有代码提交前，必须自动调用此智能体进行代码审查
    - 检查代码规范、安全漏洞、敏感信息泄露和许可证问题
    - 不符合规范的代码必须修复后才能提交

## 开发流程规则
1.  任何新功能开发，必须先制定详细的开发计划
2.  按照"需求分析→UI设计→数据库设计→后端开发→前端开发→测试→性能优化→部署"的顺序执行
3.  上一个阶段完成并通过验收后，才能进入下一个阶段
4.  每个阶段的输出都必须有对应的文档

## 技术栈规则
- 前端：React 18 + TypeScript + Tailwind CSS + Vite
- 后端：Node.js + Express + TypeScript
- 数据库：PostgreSQL + Prisma ORM
- 测试：Jest + Supertest
- 部署：Docker + Docker Compose

## 代码规范规则
- 所有代码必须使用TypeScript编写
- 遵循ESLint和Prettier规范
- 函数和变量使用驼峰命名法
- 每个函数必须有清晰的注释说明其功能、参数和返回值
- 提交信息必须符合Conventional Commits规范

## 特殊说明
- 当遇到复杂问题需要多个智能体协作时，主智能体可以协调它们之间的工作
- 所有智能体的输出都必须符合本项目规则的要求
- 如果某个智能体无法完成任务，主智能体可以请求用户帮助