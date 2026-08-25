# 已有应用的用户重新授权

refresh token 过期不代表应用配置丢失。不要把“创建或配置应用”“自动刷新 token”“用户重新授权”混为一谈。

## 先判断状态

处理认证问题时，先运行：

```bash
lark-cli profile list
lark-cli --profile <name> config show
lark-cli --profile <name> auth status --json --verify
```

根据结果选择且只选择一条流程：

| 状态 | 含义 | 操作 |
|---|---|---|
| profile 不存在，或没有 `appId` / `appSecret` | 首次配置应用 | 运行 `config init --new`；组织应用可能需要管理员审批应用 scopes |
| `identities.user.verified == true`，包括可成功刷新后的 `needs_refresh` | refresh token 仍有效 | 继续调用 user API，让 CLI 自动刷新；不要重新登录，不要重新配置应用 |
| profile 和 `appId` 存在，但 user 为 `missing` / `expired`，并提示 refresh token expired | 已有应用的用户 refresh token 过期 | 复用同一 profile 和原应用，只对已批准的最小 scopes 发起 user device-flow 重新授权 |
| API 返回真正缺少的新 scope | 应用或用户缺少权限 | 只请求错误中列出的最小 scope；如果应用后台尚未批准该 scope，才需要管理员处理 |

## refresh token 过期时重新授权

这是用户重新登录，不是创建新应用。必须保留原 profile 与 `appId`：

1. 从 `auth status` 的 `identities.user.scope` 和当前任务中确定已批准且确实需要的最小 scopes。
2. 使用同一 profile 发起 split-flow：

   ```bash
   lark-cli --profile <name> auth login \
     --scope "<already-approved-scope-1> <already-approved-scope-2>" \
     --no-wait --json
   ```

3. 用户确认授权后，使用同一 profile 完成登录：

   ```bash
   lark-cli --profile <name> auth login --device-code <device_code>
   ```

4. 再运行 `lark-cli --profile <name> auth status --json --verify`，确认 `identities.user.status == "ready"`、`tokenStatus == "valid"`、`verified == true`，并向用户报告实际 user identity。

## 权限边界

- 组织管理员批准的是应用可使用的 scopes；组织用户随后授权该已批准应用。refresh token 过期时，请求原来已批准的 scopes 通常只会重新签发 user/refresh token。若完成命令显示“本次新授予 scopes: （空）”，应明确告知用户没有新增权限。
- 除非用户明确要求首次获取全部权限并知晓可能触发管理员审批，否则不得用 `--domain all` 恢复过期 token。
- 不得为了恢复 token 而运行 `config init --new`。
- 不得默认扩大权限。`--domain all` 可能把尚未批准的 scopes 带入授权页，导致不必要的管理员申请。
- split-flow 的发起与完成必须使用同一 profile；多 profile 时不得省略 `--profile`。
