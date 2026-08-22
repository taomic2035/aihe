# WatchOS Thin Client — aihe

> SwiftUI thin client, 仅文本+推送，不跑本地模型。

## 功能
- `GET /v1/watch/sync` 拉取增量记忆/消息
- `POST /v1/watch/push` 接收云推送
- `POST /v1/watch/ingest` 上报心率/睡眠 via HealthKit

## 结构
- `WatchApp.swift` — 主入口
- `WatchView.swift` — 列表 + 发送文本
- `WatchSync.swift` — 同步逻辑

## 编译
Xcode 15+ 打开 `watchos/aiheWatch.xcodeproj`，target 选 WatchOS Simulator，Run。

## 与后端联调
```swift
let sync = WatchSync(baseURL: "https://aihe.cloud", userId: "u1")
sync.sync(since: lastVersion) { delta in
  // 更新 UI
}
```

## 模拟器演示（无真机）
`scripts/demo_watchos.sh` 用 curl 模拟手表请求。
