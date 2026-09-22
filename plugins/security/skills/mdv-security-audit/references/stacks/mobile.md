# Stack checklist: mobile

Stack-specific deep-dive items. Subagents pull from here when `app_class = mobile`. Generic focus-area checklists are in `agents/security-auditor.md`; this file lists patterns that **only** make sense for an app distributed through an app store.

## Frameworks covered

Swift/SwiftUI + UIKit, Kotlin/Java + Jetpack Compose, React Native, Flutter, Capacitor/Cordova, Xamarin/MAUI, Unity.

## The one thing to get right

The app binary is public and the device may be rooted, so **client-side checks are advisory and every secret in the bundle is disclosed.** The findings that matter are: what an *other app on the same device* can reach (exported components, deeplinks, IPC), what survives on disk unencrypted, and whether the backend re-validates everything the client claims.

## Framework-specific issues

### Android

- **Exported components** — `android:exported="true"` (required explicitly from API 31) on an `Activity`, `Service`, `Receiver`, or `Provider` that was meant to be internal. Any installed app can invoke it.
- **`ContentProvider` with `grantUriPermissions` or no permission** → data leak or write; check `android:readPermission`/`writePermission`.
- **Implicit deeplink hijack** — an `intent-filter` with an `http(s)` scheme and no App Links verification (`android:autoVerify="true"` plus a hosted `assetlinks.json`) can be claimed by another app.
- **`PendingIntent` without `FLAG_IMMUTABLE`** and with an implicit base intent → intent redirection.
- **`WebView` with `setJavaScriptEnabled(true)` plus `addJavascriptInterface`** → remote page reaching native. Also check `setAllowFileAccess`, `setAllowFileAccessFromFileURLs`, `setAllowUniversalAccessFromFileURLs`, and `loadUrl` with a user-controlled URL.
- **`onReceivedSslError` calling `handler.proceed()`** → TLS validation disabled.
- **`android:debuggable="true"`** or `android:allowBackup="true"` (backup lets `adb` extract app data) in the release manifest.
- **`usesCleartextTraffic="true"` / permissive `network_security_config.xml`** with `cleartextTrafficPermitted` or a debug-overrides trust anchor shipped in release.
- **Secrets in `strings.xml`, `BuildConfig`, or `local.properties` compiled into the APK.**
- **External storage for sensitive files** (`getExternalFilesDir`, `MediaStore`) — world-readable on older APIs and user-accessible everywhere.
- **`SharedPreferences` in plaintext** for tokens — `EncryptedSharedPreferences` or Keystore is the fix.
- **Keystore misuse** — key generated without `setUserAuthenticationRequired` where the threat model expects it, or `setInvalidatedByBiometricEnrollment(false)`.
- **Custom `TrustManager` accepting all certs** (`checkServerTrusted` empty) — often left from testing.
- **Exported `tapjacking` surface** — sensitive screens without `filterTouchesWhenObscured`.

### iOS

- **Keychain accessibility class too broad** — `kSecAttrAccessibleAlways` / `AfterFirstUnlockThisDeviceOnly` where `WhenUnlockedThisDeviceOnly` is appropriate; and missing `kSecAttrAccessControl` for biometric-gated items.
- **`UserDefaults` for tokens/PII** — an unencrypted plist in the container.
- **`ATSRequiresCertificateTransparency` / `NSAllowsArbitraryLoads: true`** in `Info.plist` shipping in release.
- **Custom URL scheme without validation**, and **Universal Links without a verified `apple-app-site-association`.**
- **`WKWebView` with `allowFileAccessFromFileURLs`, `javaScriptCanOpenWindowsAutomatically`, or a `WKScriptMessageHandler` reachable from remote content.**
- **`UIWebView`** at all — deprecated and unpatched.
- **Pasteboard** — `UIPasteboard.general` for sensitive values (system-wide, and Universal Clipboard syncs it across devices).
- **Missing `isSecureTextEntry`** and no screenshot suppression on sensitive screens (app switcher snapshots land on disk).
- **`URLSession` delegate calling `completionHandler(.useCredential, ...)` unconditionally** → pinning/validation bypass.
- **Secrets in `Info.plist`, build settings, or an embedded `.plist`.**

### React Native / Capacitor / Cordova

- **`AsyncStorage` for tokens** — plaintext SQLite/file; use Keychain/Keystore bindings.
- **JS bundle is readable** — treat every constant in it as public; check `react-native-config`/`.env` usage.
- **`__DEV__`-only guards absent** — dev menu, Flipper, or Metro reachable in release.
- **`WebView` `originWhitelist={['*']}`** and `injectedJavaScript` combined with remote content.
- **Cordova `<access origin="*">` / permissive `allow-navigation`.**
- **Native bridge modules exposing file or shell operations** to JS without validation.
- **Over-the-air JS updates (CodePush / Expo Updates)** without signature verification → RCE via update channel.

### Flutter

- **`shared_preferences` for secrets** — use `flutter_secure_storage`.
- **`HttpOverrides` / `badCertificateCallback => true`** disabling TLS validation.
- **Secrets in Dart `const`s** — present in the snapshot; `--dart-define` does not hide them either.
- **`InAppWebView` with JS handlers** reachable from remote origins.

## Cross-platform

- **Every client-side check re-verified server-side** — price, quantity, role, entitlement, receipt. "The app prevents it" is not a control.
- **Certificate pinning** — present? and is there a documented rotation plan? Absent pinning is a finding only when the threat model includes a hostile network *and* high-value data; say which.
- **Token lifetime and refresh** — long-lived non-rotating refresh tokens on a device that may be lost.
- **Biometric gate implemented in UI only** — must unlock a Keystore/Keychain-held key, otherwise it is a dialog anyone can skip on a rooted device.
- **Root/jailbreak and emulator detection** — note absence, but rank low: it is a speed bump, not a boundary. Never report bypassing it as critical.
- **Logging** — `Log.d`/`NSLog`/`print` of tokens, request bodies, or PII; `logcat` is readable by tooling and crash reporters upload it.
- **Third-party SDK data flows** — analytics/ads SDKs receiving PII or device identifiers; check what is initialized before consent.
- **Deeplink parameter handling** — a path or URL from a link used in a file operation, a WebView load, or an auth callback.
- **Backup and sync** — iCloud/Google backup including the credential store or a database of PII.
- **Screen recording / accessibility abuse** on sensitive flows.

## Common false positives in mobile

- "Hardcoded API key" that is a publishable client identifier by design — Firebase `google-services.json` / `GoogleService-Info.plist`, Maps browser key, RevenueCat public key, Sentry DSN, OAuth **public** client ID. The real question is server-side scoping; report that if missing.
- Absent obfuscation/anti-tamper as a standalone "vulnerability".
- Root detection bypass, or "attacker with a rooted device can read app memory" — that is the platform's boundary, not a defect.
- `allowBackup` / debug flags set only in a debug build type or `Debug` configuration.
- `NSAllowsArbitraryLoads` inside `NSAllowsLocalNetworking` or a dev-only scheme.
- Cleartext HTTP to a `localhost` dev server behind a build-type guard.
