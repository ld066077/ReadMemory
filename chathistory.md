user
我看了你的之后有了一点想法，我看书不是通过hermes，二十电脑的epub阅读器，并且通过跟读文本转录的英音发音来练习发音，我可以把这本epub发给hermes让他帮我记录我每天读到哪里，今天没有完成但是到哪个地方了，这样他就可以根据我的平均的阅读量安排每天的任务，并且可以记录我的读书进度，完美结合obsidian等读书笔记（我读完有什么想法可以直接发给他，他记住是在哪里我有了这个想法），这样我以后可以看到（或是让他去找？可能比较繁琐），重点是阅读英文，提升英语能力，再加上单词的记录，每天给他说几个内容中不会的单词，他帮我记录，或是感觉好的句子想要记住，让他帮我记住，形成一个数据库，之后在日报/其他地方展示给我/让我记住那个单词，这样不是完全依赖一个hermes agent（因为我学习主要还是我学习的过程，没必要为了生态封闭去开发的那么复杂），又可以让他帮助我学习中遇到的痛点（记录，记忆连接），这样的工具有没有搞头？
ai
有搞头，而且你这个想法比“让 Hermes 变成一个全能英语学习 App”更有产品感。

它的核心不是：

> “我用 Hermes 读书。”

而是：

> “我用我喜欢的工具读书，Hermes 负责记录、连接、提醒、复习、证明我在进步。”

这很重要。因为真正的学习发生在你读 EPUB、听英音跟读、做笔记、查单词、产生想法的过程中。Hermes 不应该替代这个过程，而应该做一个**外挂式学习记忆系统**。

我会把它定位成：

## Hermes：英语阅读的学习飞行记录仪

你读书，Hermes 记录飞行轨迹。

你遇到单词，Hermes 帮你沉淀。

你喜欢句子，Hermes 帮你保存并复习。

你有想法，Hermes 帮你和原文位置绑定。

你断更了，Hermes 帮你恢复节奏。

---

# 这个方向为什么有搞头

因为它解决的是英语阅读学习里非常真实的痛点：

1. **读到哪里忘了**
2. **每天读多少没有记录**
3. **不会的词分散在各处**
4. **好句子复制了但之后不看**
5. **Obsidian 笔记和原文位置脱节**
6. **读了很多，但看不见进步**
7. **学习工具太多，数据不互通**

你这个思路的好处是：Hermes 不需要做阅读器、不需要做词典、不需要做 TTS、不需要做 Obsidian 的替代品。

它只需要做一层：

> **学习记忆层 + 进度管理层 + 复习调度层。**

这反而更轻、更开放，也更容易长期用。

---

# 最好的产品形态：不要做“App”，先做“学习 Agent + 数据库”

我建议第一版不要急着做一个完整 App，而是做成一个可以和现有工具配合的系统。

## 用户每天只需要告诉 Hermes 这几类信息

### 1. 今天读到哪里

例如你说：

> 今天读《Animal Farm》第 2 章，从 “The pigs did not actually work...” 读到 “Snowball and Napoleon disagreed at every point.”

Hermes 做几件事：

* 在 EPUB 文本里定位这段；
* 记录起点和终点；
* 估算今天阅读量；
* 更新总进度；
* 根据最近 7 天平均阅读量安排明天任务。

它甚至可以说：

> 你最近平均每天读 1,250 词。按这个速度，这本书还需要 12 天读完。明天建议读到 “The animals were not certain what the word meant.”

---

### 2. 今天不会的单词

你说：

> 今天不会的词：harness, ensconce, grudgingly, pasture

Hermes 不只是记单词，而是保存成这种结构：

```text
word: grudgingly
meaning in context: 不情愿地
source: Animal Farm, Chapter 2
original sentence: They accepted it grudgingly.
status: new
next review: tomorrow
```

以后复习时不要孤立问：

> grudgingly 是什么意思？

而是问：

> 在《Animal Farm》这句话里，grudgingly 表示什么情绪？

这样单词和阅读场景绑定，记忆会强很多。

---

### 3. 今天想记住的句子

你说：

> 记一下这句：All animals are equal.

Hermes 保存：

* 原句；
* 所在书籍和章节；
* 你的中文理解；
* 可选：句型、表达价值、可模仿句；
* 未来复习提醒。

比如它可以生成：

```text
原句：All animals are equal.
用途：简洁、有力量的判断句。
可模仿：
All ideas are not equally useful.
All habits are shaped by repetition.
```

这样“好句子”不是收藏，而是变成表达素材。

---

### 4. 今天读完后的想法

你说：

> 我觉得这里 Napoleon 像是在利用信息差建立权威，这个点可以记一下。

Hermes 应该自动追问或自动绑定：

> 这个想法要绑定到你刚才读到的段落吗？

然后存成 Obsidian 里的一条笔记：

```markdown
## Thought: Napoleon 利用信息差建立权威

Book: Animal Farm
Chapter: 2
Location: paragraph containing "The pigs now revealed..."
Date: 2026-05-20
Tags: #reading/animal-farm #idea/power #english-reading

我的想法：
Napoleon 像是在利用信息差建立权威。动物们不理解文字和规则，所以权力自然集中到少数“解释者”手里。
```

这就非常有价值，因为你的想法不再是孤立笔记，而是和原文上下文绑定。

---

# 关键功能不是“聊天”，而是“定位”

你这个产品最关键的技术点其实是：

## Hermes 要能知道你说的内容在书里哪里

因为你不用 Hermes 阅读，而是用电脑 EPUB 阅读器，所以 Hermes 必须有一个“定位机制”。

可以有几种方式。

---

## 方式一：上传 EPUB，Hermes 建立书籍索引

你把 EPUB 发给 Hermes。

Hermes 不替你阅读，但会解析出：

* 章节；
* 段落；
* 句子；
* 大致位置；
* 全文搜索索引。

之后你每天只要复制一句当前读到的原文，它就可以定位。

例如：

> 今天读到 “The mystery of where the milk went to was soon cleared up.”

Hermes 搜索 EPUB，找到它在 Chapter 2，然后更新进度。

这是最自然的方式。

---

## 方式二：用“原文片段”作为锚点

不要依赖页码。因为 EPUB 在不同阅读器、字号、窗口大小下页码可能变化。

更可靠的是存：

```text
book_id
chapter
anchor_quote
before_quote
after_quote
progress_percentage
date
```

也就是说，Hermes 记录的不是“第 18 页”，而是：

> 读到包含这句话的段落。

这样以后就算换阅读器，也还能找回位置。

---

## 方式三：和 Obsidian 打通

这可能是很好的差异化。

比如 Hermes 每天自动生成一个 Obsidian 日志：

```markdown
# English Reading Log - 2026-05-20

## Book
Animal Farm

## Progress
Chapter 2  
From: "The pigs did not actually work..."
To: "Snowball and Napoleon disagreed at every point."

Estimated words read: 1,180  
Reading time: 24 min  
Status: unfinished / completed

## New Words
- grudgingly
- harness
- pasture
- ensconce

## Sentences
- All animals are equal.

## Thoughts
- Napoleon 利用信息差建立权威。

## Tomorrow
Read from: "Snowball and Napoleon disagreed at every point."
Target: 1,200 words
```

这比一个封闭 App 更有吸引力，因为它进入的是用户已有的知识库。

---

# 我认为这个产品最强的名字/概念

不是“AI 英语助手”，而是：

## Reading Memory Layer

或者中文：

## 英文阅读记忆层

它管的不是“读”，而是读书过程中产生的所有学习痕迹：

* 进度；
* 单词；
* 句子；
* 想法；
* 跟读记录；
* 复习计划；
* 阅读节奏；
* 周报。

这很像一个专门为英语阅读设计的“学习数据库”。

---

# MVP 可以非常小

第一版不要做太多。只做这个闭环：

## 上传一本 EPUB → 每天报进度 → 记录单词/句子/想法 → 自动生成复习和日报

### MVP 功能清单

1. 上传 EPUB；
2. Hermes 解析章节和全文；
3. 用户每天发送：

   * 今天读到哪里；
   * 不会的词；
   * 好句子；
   * 想法；
4. Hermes 自动定位原文位置；
5. 自动更新阅读进度；
6. 自动生成 Obsidian Markdown；
7. 每天/每周生成复习任务。

这已经足够有价值。

---

# 一个典型使用流程

### 第一天

用户上传《Animal Farm.epub》。

Hermes：

> 我已经识别到全书 10 章，约 30,000 词。
> 如果你每天读 1,000 词，大约 30 天读完。
> 明天建议从 Chapter 1 开始，读到 “...” 这一段。

---

### 第二天

用户说：

> 今天读了 Chapter 1，读到 “Man is the only creature that consumes without producing.”
> 不会的词：ensconce, lantern, knacker
> 喜欢这句：Man is the only creature that consumes without producing.
> 想法：这里像是在建立一种政治动员的语言。

Hermes：

> 已记录。你今天约读了 1,350 词，比计划多 22%。
> 这句话我已保存为“可模仿表达”。
> 你的想法已绑定到 Chapter 1 的 Old Major 演讲部分。
> 明天建议读到 Chapter 2 的 “...”
> 明天会复习 ensconce / lantern / knacker。

---

### 一周后

Hermes 生成周报：

```text
本周阅读：
- Animal Farm Chapter 1-3
- 共约 8,400 词
- 平均每天 1,200 词
- 2 天未完成计划，但都完成了最低阅读任务

词汇：
- 新增 37 个词
- 已复习 21 个
- 仍不稳定：grudgingly, harness, pasture

句子：
- 收藏 9 句
- 可用于口语表达的有 4 句

阅读能力变化：
- 每 1,000 词查词数从 18 个下降到 13 个
- 复述长度从 35 秒提升到 67 秒
```

这个周报会非常有成就感。

---

# 加上跟读发音，产品会更完整

你提到你用文本转录的英音发音来跟读，这个也可以接入 Hermes，但不要让它变重。

Hermes 可以只记录：

* 今天跟读了哪几句；
* 哪些句子读得不顺；
* 哪些词发音卡住；
* 下次重复练哪几句。

例如你说：

> 今天跟读了 Chapter 2 里 “The pigs did not actually work...” 这一段，读得不顺的是 actually, supervision, assumed。

Hermes 记录：

```text
Pronunciation practice:
source: Animal Farm, Chapter 2
sentence: The pigs did not actually work...
problem words: actually, supervision, assumed
accent target: British English
next drill: tomorrow
```

然后第二天它提醒你：

> 今天先复读昨天卡住的三个词：actually, supervision, assumed。
> 然后再读新段落。

这样发音训练和阅读进度也连起来了。

---

# 这个产品要避免的坑

## 坑 1：做成又一个阅读器

不要。

用户已经有 EPUB 阅读器了。你要做的是“旁边那个懂我读到哪的 Hermes”。

---

## 坑 2：过度自动化

如果一开始就想自动监听阅读器、自动识别位置、自动同步所有笔记，会很复杂。

第一版可以允许用户手动说：

> 今天读到这句。

只要 Hermes 能定位并记录，就已经够用了。

---

## 坑 3：只做数据库，没有督学

如果只是保存单词和句子，用户很快会堆积但不复习。

Hermes 必须每天主动做一件事：

> 今天只复习 5 个词、1 个句子、读 800 词。

这才是 agent 的价值。

---

## 坑 4：让用户输入太麻烦

每天输入必须极简。

理想格式可以是：

```text
读书打卡：
书：Animal Farm
到：Man is the only creature that consumes without producing.
词：ensconce, lantern, knacker
句：Man is the only creature that consumes without producing.
想法：Old Major 的演讲像政治动员。
```

Hermes 自动结构化，不要让用户填表。

---

# 我会把它拆成三个层次

## 第一层：记录层

回答：

> 我读到哪里了？
> 我今天学了什么？
> 我收藏了什么？
> 我产生了什么想法？

这是最基础的。

---

## 第二层：复习层

回答：

> 我什么时候该复习哪个词？
> 哪些句子值得再读？
> 哪些发音问题反复出现？
> 哪些书中表达可以转化成口语？

这是学习效果的核心。

---

## 第三层：洞察层

回答：

> 我的阅读速度有没有提升？
> 查词频率有没有下降？
> 哪些类型的词总是不认识？
> 我读哪些书最容易坚持？
> 我的英语表达有没有变自然？

这是长期留存的核心。

---

# 一个很强的产品口号

我觉得可以这样讲：

> Hermes 不替你读书。
> Hermes 让你读过的每一页都留下痕迹。

或者：

> 你负责阅读，Hermes 负责记忆、复习和进步证明。

这个方向非常清晰。

---

# 是否值得做？

我觉得值得做，但前提是你要把边界守住。

不要做：

* 完整阅读器；
* 完整词典；
* 完整课程系统；
* 完整社交社区；
* 完整 AI 老师。

先做：

## “英文原著阅读的进度 + 单词 + 句子 + 想法 + Obsidian 同步”

这一个点已经很锋利。

它的目标用户也很明确：

> 已经有一定英语基础，想读英文原著，但需要记录、复习、督促和长期积累的人。

这类用户比“零基础学英语”的用户更适合早期产品，因为他们已经有学习动机，只是缺少一个外部系统帮他们坚持和沉淀。

---

# 最小产品可以长这样

我会设计成四个入口：

### 1. `/progress`

记录阅读进度。

> `/progress Animal Farm 到 "Man is the only creature..."`

---

### 2. `/word`

记录单词。

> `/word grudgingly, harness, pasture`

---

### 3. `/sentence`

记录好句。

> `/sentence All animals are equal.`

---

### 4. `/thought`

记录想法。

> `/thought 这里像是在讲权力如何通过语言建立。`

然后 Hermes 自动问一句：

> 这个想法绑定到你刚刚读到的位置吗？

用户只要回答：

> 是。

就完成了。

---

# 更进一步：它可以变成你的“英语知识库操作系统”

长期来看，Hermes 能帮你形成几个数据库：

1. **Books Database**：读过/在读/想读的英文书；
2. **Reading Sessions**：每天读了哪里；
3. **Vocabulary Database**：从真实阅读中遇到的词；
4. **Sentence Bank**：你想模仿的英文句子；
5. **Thought Notes**：你对书的理解和想法；
6. **Pronunciation Drills**：你跟读时卡住的句子；
7. **Review Queue**：今天该复习什么。

这就不只是一个英语助手，而是一个长期成长系统。

---

## 我的判断

**有搞头，而且方向是对的。**

更准确地说，它不是一个“AI 学英语 App”的机会，而是一个：

> **面向认真读英文原著用户的学习记忆基础设施。**

你这个想法最好的地方在于：它尊重用户自己的学习流程，不强迫用户进入 Hermes 的封闭生态。Hermes 只在关键痛点上出现：记录、定位、连接、复习、提醒、总结。

这类工具如果做得足够顺手，会很有粘性。因为一旦用户的英文阅读史、单词库、句子库、想法库都沉淀在里面，Hermes 就真的变成了一个“懂我如何学习英语”的私人助手。

user
有没有类似的竞品出现？ 不一定用obsidian，能够连接现有的最好用的hermes的外接记忆系统也很好

ai
有，而且不少。但**完全像你说的这个“外接记忆系统 + 英文阅读进度 agent”**，我暂时没看到非常成熟的同类。现有产品大多只覆盖其中一块。

我的判断是：

> **LingQ 最像“英语阅读学习平台”；Readwise 最像“外接阅读记忆系统”；Anki 最像“复习引擎”；Obsidian/Logseq/Notion 最像“长期知识库”；但还缺一个 Hermes 这样的 agent 把它们串起来。**

---

## 1. 最接近的直接竞品：LingQ

**LingQ 是最接近“读真实内容学语言”的产品。**

它允许用户用真实内容学习语言，包括书、播客、视频等；官方也强调它会记录词汇增长、阅读/听力活动和学习进度。它的核心思路和你说的“通过英文原著提升英语能力”很接近。([lingq.com][1])

但问题是：**LingQ 想把你拉进它自己的阅读环境。**

你要把书导入 LingQ，在 LingQ 里阅读、点词、标记已知词、统计进度。对很多语言学习者这很好，但和你的想法不同。你想要的是：

> 我仍然用自己喜欢的 EPUB 阅读器、TTS、Obsidian；Hermes 只做记录、记忆、连接和复习。

所以 LingQ 是强竞品，但也是一个很好的反面参照：
**Hermes 不应该做成 LingQ 2.0，而应该做成“LingQ 的外接 agent 版”。**

---

## 2. Readlang：轻量版 LingQ

**Readlang 也很接近。**

它主打“通过阅读学习语言”：用户可以在网页、文章、书籍里点击单词或短语翻译，并自动生成词汇闪卡。([readlang.com][2])

它的问题也类似：

* 更像一个阅读/查词工具；
* 重点在 click-to-translate 和 flashcards；
* 没有很强的“个人读书进度 agent”；
* 没有你说的“今天读到哪、想法绑定到原文位置、日报、Obsidian 记忆层”这个系统感。

所以 Readlang 是相邻竞品，但不是你这个方向的完整竞品。

---

## 3. Lute / Learning Using Texts：开源自托管版 LingQ

**Lute 很值得看。**

Lute 是一个开源、自托管的“通过文本学习语言”工具，核心功能包括定义语言和词典、创建/编辑文本、创建词条和多词表达。([GitHub][3])

它对高级用户有吸引力，因为它更开放、更可控，也更接近“我有自己的文本，我想围绕文本建立词汇系统”。

但它仍然是：

> 你把文本放进 Lute，在 Lute 里读。

而你的 Hermes 想法是：

> 用户可以在任何地方读，Hermes 只负责识别位置、沉淀数据、组织复习。

所以 Lute 对产品设计很有参考价值，尤其是词汇状态、上下文词条、多词表达这些功能；但它不是“全天候外接记忆 agent”。

---

## 4. Readwise + Reader：最强的“外接阅读记忆系统”

如果不限定英语学习，**Readwise / Reader 是最危险的相邻竞品**。

Readwise Reader 是一个面向重度阅读者的 read-it-later / 阅读收集工具，可以处理网页文章、PDF、newsletter、RSS、EPUB、YouTube 等内容；Readwise 本体负责高亮、笔记、每日回顾和知识留存。([Readwise][4])

它更关键的是外部同步能力：Readwise 官方支持把 highlights 导出到 Obsidian、Notion、Evernote、Roam 等工具，也有官方 Obsidian 插件，可以持续同步新高亮，而且不会覆盖 Obsidian 里的旧内容。([Readwise Docs][5])

Readwise 还有 API，可以创建、获取、更新 highlights；Reader 也有 API。([Readwise][6])

所以如果你问：

> “有没有能连接现有最好用的 Hermes 外接记忆系统？”

我会说：**Readwise 是最值得研究的外接记忆 hub。**

但 Readwise 的问题是：

* 它不是英语学习产品；
* 它主要围绕 highlights 和 notes，不是围绕“语言习得”；
* 它不会天然记录“今天英文原著读到哪一句”；
* 它不会把单词、句子、想法、发音练习、每日任务整合成一个英语成长系统；
* 它更适合“知识工作者阅读”，不专门服务“英文原著学习者”。

所以 Hermes 的机会可以是：

> **Readwise 是记忆库，Hermes 是学习教练和数据解释层。**

---

## 5. Anki / VocabSieve：复习引擎和 sentence mining 工具

**Anki 是绕不开的。**

Anki 官方定位是智能闪卡程序，让用户把时间更多花在困难材料上，减少已经掌握内容的复习。([Anki][7])

围绕 Anki 有很多语言学习工具。例如 VocabSieve 是一个 Anki companion，主打 sentence mining：从文本、视频、电子书高亮等来源收集包含目标词的句子，再做成长期复习材料。([GitHub][8])

这类工具和你的想法有重叠：

* 记录不会的词；
* 保存上下文句子；
* 做成复习材料；
* 不完全依赖单一学习 App。

但它们通常更偏技术流和工具流，不像 Hermes 这种“你用自然语言告诉我今天读了什么，我帮你整理、复习、规划”的 agent 体验。

所以这里的机会是：

> **Hermes 不一定要重做 Anki，而是可以把 Anki 当作复习后端。**
> Hermes 负责理解、整理、选择今天该复习什么；Anki 负责稳定的 spaced repetition。

---

## 6. Kindle / KOReader / Koodo Reader：阅读器侧的相邻方案

如果用户愿意换阅读器，已经有一些阅读器在做类似功能。

例如 Koodo Reader 支持 EPUB、PDF、MOBI、AZW3 等格式，也有文本转语音、翻译、词典、阅读统计、书签、笔记和高亮。([GitHub][9])

KOReader 是开源电子书阅读器，支持 EPUB、PDF、MOBI 等多种格式，也有导出 highlights / notes、Joplin 集成、flashcard trainer 等能力。([KOReader][10])

但这些产品的方向还是：

> 阅读器本身变强。

而你想做的是：

> 不管用户用什么阅读器，Hermes 都能成为旁边那个记忆和督学层。

这两者不冲突。甚至 Hermes 可以先不做阅读器，只做对接：

* 复制一句当前读到的原文 → Hermes 定位；
* 导入 EPUB → Hermes 建索引；
* 导出 Markdown → Obsidian；
* 导出 cards → Anki；
* 生成日报/周报 → Telegram/邮件/Notion/Obsidian。

---

## 7. Migaku / Language Reactor：更偏“沉浸式输入 + 句子挖掘”

**Migaku 和 Language Reactor 更偏视频、网页、字幕和 sentence mining。**

Language Reactor 主打从 Netflix、YouTube 等原生材料中学习语言，可以保存字幕短语、保存带上下文的单词，并做导出。([languagereactor.com][11])

Migaku 是一个浏览器扩展，把网站、字幕和文本变成语言学习材料；它也在移动端引入 Reader 功能，用于读书、查词、制卡和 TTS。([migaku.com][12])

这类工具很强，但更像：

> “我看视频/网页时顺手学语言。”

你的方向更像：

> “我长期读英文书，Hermes 维护我的阅读成长档案。”

所以 Migaku / Language Reactor 对“句子挖掘、上下文词汇、音频/字幕学习”有参考价值，但不完全覆盖“读书进度 + 想法绑定 + 外接知识库”的场景。

---

## 8. NotebookLM / Mem / Obsidian：AI 记忆和知识库侧

如果看“外接记忆系统”，还有一类是 AI 笔记和知识库。

NotebookLM 是 Google 的源材料驱动 AI 工具，官方说它是 grounded in your own documents，可以围绕上传来源进行问答、总结和生成内容。([blog.google][13])

Mem 则更偏 AI notes / thought partner，主打把想法、会议、研究材料放进去，然后通过 AI 自动组织和召回。([get.mem.ai][14])

Obsidian 则是本地 Markdown 知识库，官方强调它基于本地纯文本 Markdown 文件，并用链接建立个人知识网络。([Obsidian][15])

这些工具的优势是“记忆”和“检索”，但它们没有天然的英语学习闭环：

* 不会自动判断今天该读多少；
* 不会根据 EPUB 位置安排任务；
* 不会把单词做成语境复习；
* 不会记录跟读发音问题；
* 不会把“读到哪里产生什么想法”作为核心数据结构。

所以 Hermes 可以把它们当作后端，而不是竞品正面对抗。

---

# 我觉得最像你想法的“现有组合”

如果今天不用开发，只用现有工具拼一个最接近的系统，大概是：

## 方案 A：Readwise + Obsidian + Anki + ChatGPT/Hermes

这是最接近你想法的组合。

* **Readwise**：存高亮、句子、摘录；
* **Obsidian**：做长期笔记库；
* **Anki**：做单词/句子复习；
* **Hermes**：每天听你汇报进度，帮你定位、整理、安排任务、生成日报。

这个组合的缺点是：需要你手动维护很多流程。
Hermes 的机会就是把这些流程变成自然语言操作。

---

## 方案 B：LingQ + Anki / NotebookLM

如果用户愿意在 LingQ 里读书，这个方案很强。

* LingQ 负责阅读、听力、词汇统计、进度；
* Anki 负责深度复习；
* NotebookLM 负责围绕书本问答和总结。

缺点是：阅读体验被 LingQ 接管，和你“不想为了生态封闭而换工具”的想法冲突。

---

## 方案 C：KOReader + VocabSieve + Anki + Obsidian

这是技术型用户方案。

* KOReader 负责 EPUB/PDF 阅读；
* VocabSieve 或插件负责 sentence mining；
* Anki 负责复习；
* Obsidian 负责笔记。

优点是开放、可控。
缺点是安装、同步、维护成本高，不适合普通用户。

---

# 你的机会在哪里？

我觉得机会不在“再做一个阅读器”，也不在“再做一个背单词 App”。

机会在这个中间层：

## Hermes English Memory Layer

它连接：

```text
EPUB 文件
↓
阅读位置锚点
↓
单词 / 句子 / 想法 / 跟读记录
↓
Obsidian / Readwise / Notion / Anki
↓
日报 / 周报 / 复习任务 / 进度预测
```

现在的竞品大多是下面几种：

| 类型     | 代表产品                                   | 强项                     | 缺口               |
| ------ | -------------------------------------- | ---------------------- | ---------------- |
| 语言阅读平台 | LingQ, Readlang, Lute                  | 读文本、查词、词汇追踪            | 要在它们里面读          |
| 阅读记忆系统 | Readwise Reader                        | highlights、notes、同步知识库 | 不专门服务英语学习        |
| 间隔复习   | Anki, VocabSieve                       | 单词/句子复习                | 不懂你的阅读进度和想法      |
| 阅读器    | Koodo, KOReader, Kindle                | 阅读体验、标注、部分统计           | 不像 agent 一样规划和复盘 |
| AI 知识库 | NotebookLM, Mem, Obsidian AI workflows | 搜索、问答、总结               | 没有学习督导和 SRS 闭环   |

你的 Hermes 可以做的是：

> **不替代任何一个工具，而是把它们变成一个学习系统。**

---

# 我会怎么定位，才能避开竞品

不要说：

> “我们是 AI 英语阅读器。”

这会撞 LingQ、Readlang、Migaku、Koodo。

也不要说：

> “我们是 AI 笔记工具。”

这会撞 Notion、Obsidian、Mem、NotebookLM。

更好的定位是：

## “给英文原著学习者的外接记忆和复习 agent”

或者更锋利一点：

## “不换阅读器，也能拥有 LingQ 式英语学习记录。”

这个定位很有意思，因为它直接打中一类用户：

> 我已经有自己的阅读工具、TTS、Obsidian、Anki，但我的学习数据是散的。

Hermes 的价值就是：

> 把散落的阅读进度、单词、好句、想法、跟读记录，变成一个可复习、可检索、可回顾的成长系统。

---

# 最值得防的竞品：Readwise

如果你以后真的做这个，我觉得最值得防的不是 LingQ，而是 **Readwise**。

LingQ 是学习平台，边界很清楚。
Readwise 是记忆基础设施，和你的“外接记忆系统”更接近。

Readwise 已经有：

* 多来源 highlights；
* 阅读器 Reader；
* Obsidian / Notion / Roam 等同步；
* API；
* 每日回顾；
* 知识工作者用户群。

但它没有：

* 英语学习专用 schema；
* EPUB 外部阅读位置锚点；
* 单词语境复习；
* 跟读记录；
* “今天读到哪”的 agent 打卡；
* 根据个人阅读量自动安排原著计划；
* 把“想法”绑定到英文原文位置。

所以可以把 Readwise 当成潜在集成对象，而不是一开始就硬打。

---

## 最终判断

**有相邻竞品，没有完全重合的成熟竞品。**

最接近的几个是：

1. **LingQ**：最接近“读原著学语言”，但封闭在自己的阅读体验里。
2. **Readwise + Reader**：最接近“外接阅读记忆系统”，但不是英语学习产品。
3. **Anki + VocabSieve**：最接近“单词/句子复习引擎”，但不是 agent。
4. **Lute / Readlang / Migaku**：覆盖查词、阅读、sentence mining，但不主打长期读书进度和想法绑定。
5. **Obsidian / NotebookLM / Mem**：适合作为记忆库或检索层，但缺少学习计划和复习闭环。

所以这个方向是有搞头的。
真正的产品机会是做一个**开放式英语阅读学习 agent**：

> 用户继续用自己喜欢的阅读器和笔记工具；Hermes 做记录、定位、复习、提醒、总结和进步证明。

[1]: https://www.lingq.com/en/?utm_source=chatgpt.com "Learn Languages Online with Real Content | LingQ Language ..."
[2]: https://readlang.com/?utm_source=chatgpt.com "Readlang: Learn a Language by Reading"
[3]: https://github.com/LuteOrg/lute-v3?utm_source=chatgpt.com "LuteOrg/lute-v3: LUTE = Learning Using Texts: ..."
[4]: https://readwise.io/read?utm_source=chatgpt.com "The first read-it-later app built for power readers."
[5]: https://docs.readwise.io/readwise/docs/exporting-highlights/obsidian?utm_source=chatgpt.com "How does the Readwise to Obsidian export integration work?"
[6]: https://readwise.io/api_deets?utm_source=chatgpt.com "Readwise API"
[7]: https://apps.ankiweb.net/?utm_source=chatgpt.com "Anki - powerful, intelligent flashcards"
[8]: https://github.com/FreeLanguageTools/vocabsieve?utm_source=chatgpt.com "VocabSieve - Anki companion for language learning"
[9]: https://github.com/koodo-reader/koodo-reader?utm_source=chatgpt.com "koodo-reader/koodo-reader: A modern ebook manager ..."
[10]: https://koreader.rocks/?utm_source=chatgpt.com "KOReader"
[11]: https://www.languagereactor.com/?utm_source=chatgpt.com "Language Reactor"
[12]: https://migaku.com/?utm_source=chatgpt.com "Migaku - The fastest way to really learn a language"
[13]: https://blog.google/innovation-and-ai/technology/ai/notebooklm-google-ai/?utm_source=chatgpt.com "Introducing NotebookLM"
[14]: https://get.mem.ai/?utm_source=chatgpt.com "Mem – Your AI Thought Partner"
[15]: https://obsidian.md/?utm_source=chatgpt.com "Obsidian - Sharpen your thinking"

user
有。
但先说关键结论：

## 没有任何记忆系统能“确保 AI 不出错”

更现实的目标是：

> **让 AI 的每一次记忆调用都能追溯、验证、纠错。**

所以最好的系统不是“AI 记得更聪明”，而是：

> **AI 不直接相信自己的记忆；它必须从确定的数据库/原文锚点里查证，再回答。**

---

# 对 Hermes 来说，最佳方案不是纯 AI memory

如果你说的是类似 ChatGPT 自带 memory 那种能力，它适合记：

* 用户偏好；
* 学习目标；
* 常用工具；
* 最近在读什么；
* 喜欢英音；
* 想每天读英文原著。

但它**不适合**作为你英文阅读系统的核心数据库。OpenAI 自己也说明，ChatGPT memory 更适合高层偏好和细节，不应依赖它保存精确模板或大段原文；ChatGPT 也不会保留过去聊天的每个细节。([OpenAI Help Center][1])

所以 Hermes 的核心记忆应该分两层：

## 1. 确定性记忆：数据库

用来存不能错的东西：

* 今天读到哪一句；
* 书名；
* 章节；
* 原文锚点；
* 单词；
* 好句；
* 想法；
* 复习状态；
* 跟读记录。

这些不要让 AI “记在脑子里”，而要进结构化数据库。

## 2. AI 记忆：检索和解释层

用来做：

* “帮我找我之前关于 Napoleon 的想法”；
* “哪些单词我总是忘”；
* “这周我阅读节奏怎么样”；
* “把这些句子整理成复习卡片”；
* “根据我的平均阅读量安排明天任务”。

---

# 如果问“最好的现成 AI memory 是哪个？”

我会这样分：

| 需求                 | 最适合                                   |
| ------------------ | ------------------------------------- |
| 用户偏好、长期个性化         | Mem0 / Letta                          |
| Agent 长期记忆、关系和时间变化 | **Zep / Graphiti**                    |
| 大量文档问答、知识库检索       | GraphRAG / LlamaIndex / LangChain RAG |
| 准确记录阅读进度、单词、句子     | **Postgres / SQLite 这类结构化数据库**        |
| 复习调度               | Anki / FSRS 类系统                       |
| 笔记沉淀               | Obsidian / Markdown / Readwise        |

如果只让我选一个“最值得研究的 agent memory 系统”，我会选：

## Zep / Graphiti

原因是它不是简单向量库，而是**时间感知知识图谱**。Graphiti 官方介绍说，它会持续整合用户交互和业务数据，形成动态可查询的图谱，并保留历史上下文；它还结合语义搜索、关键词匹配和图遍历。([getzep.com][2])

Zep 的论文也强调它用 Graphiti 维护 episode、entity、fact 等层级，并保留原始 episode，使语义事实可以追溯到来源；它还处理时间关系和事实失效，比如新事实出现后让旧事实过期。([arXiv][3])

这对 Hermes 很重要，因为学习记忆是会变化的：

> 你以前不会 `grudgingly`，后来掌握了。
> 你以前每天读 300 词，后来每天读 1200 词。
> 你以前觉得某个角色是正面的，读到后面想法改变了。

普通向量库很难处理“什么时候是真的”。Zep / Graphiti 这类 temporal memory 更适合这种动态记忆。

---

# 但对你的产品，Zep 也不能单独解决问题

你最重要的需求是：

> AI 找到的信息不能错，尤其是读到哪里、哪个想法对应哪段原文、哪个单词来自哪句话。

这类信息不能只靠向量搜索。

比如你问：

> 我上周在《Animal Farm》里关于 Napoleon 的想法是什么？

如果只靠向量检索，AI 可能找出一段“语义相似”的内容，但不一定是你真正那条笔记。

所以 Hermes 最稳的架构应该是：

## 结构化数据库 + 原文锚点 + 混合检索 + AI 总结

不是单一 memory。

---

# 我认为 Hermes 最佳记忆架构

## 第一层：Source of Truth，真相库

这里存绝对不能错的数据。

可以用：

* SQLite，适合本地优先；
* Postgres，适合云端产品；
* Postgres + pgvector，兼顾结构化和语义检索。

数据结构大概是：

```text
Book
- book_id
- title
- author
- epub_hash
- total_words

ReadingSession
- session_id
- book_id
- date
- start_anchor
- end_anchor
- words_read
- completed_or_not

Vocabulary
- word
- book_id
- chapter
- sentence_id
- original_sentence
- user_meaning
- review_status

SentenceBank
- sentence
- book_id
- anchor
- reason_saved
- imitation_notes

Thought
- thought_text
- book_id
- anchor
- related_quote
- tags
- created_at
```

这层不需要 AI “猜”。
它就是事实。

---

## 第二层：EPUB 位置锚点

不要用页码。EPUB 页码会因为阅读器、字号、窗口大小变化而变化。

更好的办法是用：

1. EPUB CFI；
2. 章节 + 段落编号；
3. 原文 quote anchor；
4. 前后文 hash；
5. 字符 offset。

EPUB CFI 是专门用来引用 EPUB 内任意内容位置的标准化方法，W3C/EPUB 规范里也说明它用于在 EPUB 出版物内部定位内容。([W3C][4])

对 Hermes 来说，最稳的是多重锚点：

```text
book_id: animal_farm
chapter: 2
epub_cfi: ...
anchor_quote: "The pigs did not actually work..."
before_quote: ...
after_quote: ...
paragraph_hash: ...
```

这样就算 EPUB 版本略有不同，也能尽量找回位置。

---

## 第三层：混合检索

不能只用 vector search。

要用：

* 关键词搜索：找精确词、原句、书名、章节；
* 向量搜索：找语义相近的想法；
* metadata filter：限制在某本书、某章、某时间段；
* reranker：重新排序最相关结果；
* source verification：回答前检查原文是否真的支持。

LlamaIndex 对 RAG 的描述里也把加载、索引、存储、查询和评估拆成关键阶段，并强调索引和 metadata 策略会影响能否准确找到上下文。([Developer Documentation][5])

所以 Hermes 的检索应该像这样：

```text
用户问：我之前关于 Napoleon 的想法有哪些？

1. 先过滤 book = Animal Farm
2. 再过滤 note_type = thought
3. 再关键词搜 Napoleon
4. 再向量搜 “power / authority / information gap”
5. reranker 排序
6. 返回带原文锚点的结果
7. AI 只能基于这些结果总结
```

这比“AI 从记忆里想起来”可靠得多。

---

# 第四层：知识图谱，适合做连接，不适合当唯一真相源

Zep / Graphiti 可以放在这一层。

它适合帮你发现：

* 哪些想法都和 “power” 有关；
* 哪些单词来自同一类政治寓言文本；
* 你在哪些书里反复记录 “authority / obedience / propaganda”；
* 哪些人物、主题、句子、想法之间有关联。

Microsoft GraphRAG 也是类似思路：它不是普通的片段向量搜索，而是先从语料中抽取实体、关系和关键 claims，构建知识图谱，再用图结构辅助回答复杂问题。([GitHub上的微软][6])

但我不会让图谱单独保存“今天读到哪里”这种事实。
它可以做连接层，不该替代数据库。

---

# 第五层：回答必须带证据

Hermes 应该有一个硬规则：

> 没找到来源，不允许假装记得。

比如你问：

> 我昨天读到哪里了？

Hermes 应该回答：

> 我找到的最后记录是：2026-05-19，《Animal Farm》Chapter 2，读到 “...”
> 如果你昨天还有额外阅读，我这里没有记录。

而不是：

> 你大概读到第二章中间。

这就是可靠系统和普通 AI 记忆的区别。

LangSmith 的 RAG 评估文档也把检索质量、答案准确性、groundedness 等作为评估维度；它还明确提到可以评估答案是否 grounded in retrieved documents。([LangChain 文档][7])

Hermes 也应该内置这种机制：

```text
每个回答都检查：
- 是否引用了具体记录？
- 是否引用了原文位置？
- 是否有未被来源支持的结论？
- 是否把“推测”标成了“事实”？
```

---

# 所以“最好的”到底是什么？

我会给你一个很明确的答案：

## 最佳整体方案

> **Postgres / SQLite 结构化真相库 + EPUB 锚点 + 混合检索 + Zep/Graphiti 关系记忆 + Anki/FSRS 复习队列。**

这不是最炫的方案，但最可靠。

---

## 如果只能选一个现成 AI memory 产品

选：

# Zep / Graphiti

因为它最适合 agent 长期记忆，尤其是：

* 时间变化；
* 人、书、想法、单词之间的关系；
* 多来源上下文；
* 不只做静态文档检索；
* 可以处理旧事实失效。

但要注意：
**Zep/Graphiti 不能替代你的主数据库。**

它应该作为 Hermes 的“关系记忆层”，不是“唯一记忆层”。

---

# 如果我是你，我会这样做 Hermes

## V1：先不用复杂 AI memory

先做：

```text
SQLite/Postgres
+
EPUB 全文索引
+
Obsidian Markdown 导出
+
Anki 卡片导出
+
简单向量搜索
```

这样已经能解决 80% 的核心问题：

* 记录读到哪里；
* 记录单词；
* 记录句子；
* 记录想法；
* 每天生成复习；
* 周报统计进步。

---

## V2：加入 Zep / Graphiti

当用户数据多了，再加入：

* 主题关系；
* 跨书连接；
* 动态学习画像；
* 长期趋势；
* “我在哪些地方反复思考过权力/语言/自由”。

---

## V3：加入可靠性评估

做一个 Hermes 自检系统：

```text
回答前：
- retrieval confidence
- source coverage
- citation check
- contradiction check
- unsupported claim check
```

当置信度低时，Hermes 应该说：

> 我没有找到可靠记录。
> 我可以根据最近一次记录推测，但这不是确定事实。

这才是“不会乱记”的核心。

---

# 我的最终判断

**最好的记忆系统不是某个 AI memory 产品，而是一个可验证的 memory stack。**

对 Hermes 来说：

> **数据库负责事实，Zep/Graphiti 负责关系，RAG 负责检索，AI 负责解释，引用负责校验。**

如果你要做英文阅读学习工具，最重要的不是让 Hermes “像人一样记得”，而是让 Hermes：

1. **存得准**；
2. **找得回**；
3. **说得清来源**；
4. **不确定时承认不确定**；
5. **能把单词、句子、想法和原文位置连起来。**

所以我会把最推荐方案命名为：

## Verified Memory for English Reading

中文就是：

## 可验证英文阅读记忆系统

这比单纯 “AI memory” 更有产品壁垒。

[1]: https://help.openai.com/en/articles/8590148-memory-faq "Memory FAQ | OpenAI Help Center"
[2]: https://www.getzep.com/product/open-source/ "Graphiti Open Source - Zep | Zep"
[3]: https://arxiv.org/html/2501.13956v1 "Zep: A Temporal Knowledge Graph Architecture for Agent Memory"
[4]: https://w3c.github.io/epub-specs/epub33/epubcfi/?utm_source=chatgpt.com "EPUB Canonical Fragment Identifiers 1.1"
[5]: https://developers.llamaindex.ai/python/framework/understanding/rag/ "Introduction to RAG | Developer Documentation"
[6]: https://microsoft.github.io/graphrag/ "Welcome - GraphRAG"
[7]: https://docs.langchain.com/langsmith/evaluate-rag-tutorial "Evaluate a RAG application - Docs by LangChain"
