# 🎮 Random Dice Boss AI — HFSM Project

## 📌 專案概述 (Project Overview)
本專案設計並實作一套適用於 **Random Dice 類型遊戲**的 Boss AI 系統。  
核心目標並非追求數學上的最優策略，而是在高度隨機的遊戲環境中，打造一個**具備策略感、可控性與良好玩家體驗的 Boss 行為模型**。

為此，本專案採用 **Hierarchical Finite State Machine（HFSM，分層有限狀態機）** 作為主要 AI 架構，取代傳統的單層 FSM 或複雜的強化學習。

---

## 🎯 設計目標 (Design Goals)
- 讓 Boss 行為「看起來有在思考」。
- 避免隨機環境下 AI 行為出現不可預測的失控。
- 行為邏輯 **可解釋、可除錯、可平衡**。
- 支援快速調參與 Boss 變體設計。
- 適合團隊協作與長期維護。

---

## ❓ 為什麼不使用強化學習 (Reinforcement Learning)
Random Dice 具有以下特性：
- 棋盤配置高度隨機。
- 骰子種類、星級、位置組合龐大。
- 玩家策略差異極大（非平穩環境）。

這使得強化學習在實務上面臨：
- **狀態空間爆炸**：難以覆蓋所有隨機組合。
- **Reward 定義困難**：難以量化每一回合的細微優劣。
- **不可控性**：行為可能變得怪異且難以進行遊戲數值的平衡調整。
- **成本效益**：訓練成本與實作效益不符。

👉 因此，本專案選擇 **規則導向、可控的 HFSM 架構**，以工程與遊戲設計角度達成最佳平衡。

---

## 🧠 核心架構 — HFSM

整體 AI 架構分為三層：

**Strategy Layer (策略層) → Behavior Layer (行為層) → Action Layer (執行層)**

### 設計原則
- **上層決定方向，下層負責執行**。
- **上層可中斷下層，下層不可反向影響上層**。
- **每一層只處理「自己該思考的問題」**，降低耦合度。

---

## 🟦 Strategy Layer —「我是誰？」

**更新頻率**
- 低頻更新（約 0.5 ~ 1 秒）。

**職責**
- 根據玩家整體表現，決定 Boss 的當前作戰方針。
- 只負責「態度」的切換，不直接處理技能施放。

**策略狀態 (Strategy States)**
- `IdleStrategy`：初始或觀察狀態。
- `AggressiveStrategy`：威脅中等時，採取主動進攻。
- `DefensiveStrategy`：當玩家輸出或合成頻率過高時，轉為防守。
- `RecoveryStrategy`：Boss 血量過低時，優先尋求生存與回血。

---

## 🟩 Behavior Layer —「我要做什麼？」

**更新頻率**
- 每幀檢查，受冷卻 (Cooldown) 與忙碌 (Busy) 狀態限制。

**職責**
- 在既定的策略下，選擇最合適的具體技能或行為。
- 僅在該策略所屬的行為池中切換。

**行為範例**
- **Aggressive**：
  - 偵測到玩家高頻合成 → 使用 `Disrupt` 技能干擾。
  - 否則 → 執行 `BasicAttack` 基礎攻擊。
- **Defensive**：
  - 觸發 `Shield` (護盾) 或 `DamageReduction` (減傷)。
- **Recovery**：
  - 執行 `HealSelf` (自我治療) 或 `SummonMinion` (召喚小怪)。

**中斷機制**
- 當策略層改變狀態時，行為層會立即重置，確保行為與策略一致。

---

## 🟧 Action Layer —「我正在做什麼？」

**更新頻率**
- 每幀更新（基於計時器 Timer）。

**職責**
- **純執行層**，不參與任何 AI 決策。
- 管理技能的完整生命週期（施法時間、效果觸發、冷卻）。

**技能流程**
1. **Cast Time** (吟唱/啟動)
2. **Effect Apply** (效果套用)
3. **Cooldown / Global Cooldown** (冷卻時間)

**保護機制**
- **全域冷卻 (GCD)**：技能間的基本間隔，防止行為過於頻繁。
- **Busy 標記**：執行技能期間鎖定行為層，防止指令衝突。

---

## 📊 Player Metrics — 威脅評估系統

這是 AI 的「感知器官」，使用 **滑動窗口 (Sliding Window)** 蒐集最近 5 秒的玩家行為數據。

**關鍵指標 (Metrics)**
- `Damage Rate`：過去 5 秒內的平均秒傷。
- `Merge Rate`：過去 5 秒內的合成頻率。
- `Dice Count`：目前棋盤上的骰子密度。

**威脅評分 (Threat Score) 計算**
`Threat Score = (Damage Rate × 0.6) + (Merge Rate × 0.3) + (Dice Count × 0.1)`

**狀態切換門檻**
- `0.0 – 0.3` → Idle
- `0.3 – 0.7` → Aggressive
- `0.7 – 1.0` → Defensive

---

## ⚙️ Engineering Specification (工程規範)

### 三大金律 (DO NOT BREAK)
1. **策略層禁止直接觸發技能**：必須透過行為層仲裁。
2. **行為層禁止反向改變策略**：策略切換應獨立受 Metrics 驅動。
3. **執行層禁止包含判斷邏輯**：僅負責時間軸管理與效果套用。

### 遊戲系統整合
- `on_skill_start(skill_name)`：處理動畫觸發與視覺鎖定。
- `apply_skill_effect(skill_name)`：執行具體的數值變動（如：扣血、格子鎖定、骰子摧毀）。

---

## ✅ 總結 (Summary)
本系統透過 **HFSM 架構** 在不依賴複雜黑箱模型（如 Reinforcement Learning）的情況下，實現了具備策略深度與高度可控的 Boss AI。這套架構不僅讓遊戲更具挑戰性，也極大地降低了後期數值平衡與行為除錯的成本，是 Random Dice 類型遊戲開發的理想選擇。
