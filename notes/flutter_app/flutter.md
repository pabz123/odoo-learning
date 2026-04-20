# Flutter Guide (Assignment-Focused)

## 1) What Flutter is
Flutter is Google’s UI toolkit for building **cross-platform apps** from one codebase.

- Language: **Dart**
- UI model: everything is a **Widget**
- Targets: Android, iOS, Web, Desktop
- Big advantage for us: one mobile codebase for assignment requirements

---

## 2) How Flutter apps work
Flutter builds UI by composing widgets in a tree:

- `MaterialApp` / `CupertinoApp` at the top
- Screens as widgets (`Scaffold`, `AppBar`, `ListView`, etc.)
- State changes trigger UI rebuilds

Core idea: **data/state drives UI**.

---

## 3) Typical Flutter project structure
When you run `flutter create .`, you get:

- `lib/` → app source code
- `android/`, `ios/` → platform projects
- `pubspec.yaml` → dependencies and project metadata

For clean architecture (like your assignment), we split by feature:

- `features/auth`
- `features/application`
- `features/tracking`
- `core/` for shared constants/storage

---

## 4) State management in your assignment: BLoC
Your assignment specifically requires BLoC.

### BLoC pattern in practice
- **Event**: user action (login tapped, submit form, track request)
- **Bloc**: handles business logic and async work
- **State**: loading/success/failure/authenticated/etc.
- UI listens and updates accordingly

This keeps:
- UI clean
- business logic testable
- predictable app behavior

---

## 5) Networking in Flutter
You call backend APIs with `http`.

General flow:
1. Build request (`GET`, `POST`, multipart)
2. Parse JSON response
3. Handle status + errors
4. Emit Bloc state

For your project, the app talks to Odoo mobile APIs:

- `POST /api/mobile/signup`
- `POST /api/mobile/login`
- `GET /api/mobile/metadata`
- `POST /api/mobile/application/submit` (multipart files)
- `GET /api/mobile/application/track?reference=...`

---

## 6) Session persistence (assignment requirement)
You use `shared_preferences` to store:

- auth token
- user profile basics

So user stays logged in after app restart.

---

## 7) File upload in Flutter
You use `file_picker` + multipart upload for:

- passport photo
- LC letter

Important:
- validate file chosen before submit
- show loading state while uploading
- show friendly backend error if duplicate phone/email

---

## 8) How we are using Flutter in *this* assignment
You need 4 parts, and your implementation maps like this:

## Part 1: Authentication
- Signup screen + Login screen
- Email/phone/password validation
- Local session persistence (SharedPreferences)
- Proper error messages

## Part 2: Application Form
- 8–12 fields (name, DOB, gender, district, phone, email, etc.)
- Upload photo + LC letter
- API submission
- Show tracking number from response

## Part 3: Tracking
- Enter tracking number
- Show current status + timeline

Status mapping used:
- `new` -> Pending
- `stage1_review` -> Verified
- `stage1_approved` / `stage2_review` -> Senior Approval
- `approved` -> Final Approval
- `rejected` -> Rejected

## Part 4: BLoC Architecture
- `AuthBloc`
- `ApplicationSubmissionBloc`
- `TrackingBloc`

Each has loading/success/failure states.

---

## 9) Commands you’ll use often
After Flutter installs:

```bash
flutter doctor
cd ~/Desktop/odoo-19.0/custom_addons/national_id_application/flutter_app
flutter create .
flutter pub get
flutter run
```

Useful extras:

```bash
flutter clean
flutter pub get
flutter analyze
```

---

## 10) Common setup pitfalls (and fixes)

## `flutter: command not found`
Install and add PATH:
```bash
sudo snap install flutter --classic
echo 'export PATH="$PATH:/snap/bin"' >> ~/.bashrc
source ~/.bashrc
```

## Android emulator cannot reach localhost backend
Use:
- `10.0.2.2:8069` (Android emulator)
- real IP for physical phone on same network

## API returns HTML instead of JSON
Usually wrong URL/db/header.
Ensure:
- correct endpoint path
- `X-Odoo-Database` header set
- auth token for protected endpoint

---

## 11) Why this approach is good for your submission
- Matches assignment scope exactly
- Clean architecture and clear separation
- Easy to demo each requirement (Auth, Submit, Track, BLoC states)
- Easy to explain in viva/report

---

## 12) Quick demo checklist
1. Signup user
2. Login success + session retained
3. Submit application with files
4. Display tracking number
5. Track and show stage timeline
6. Show friendly error example (duplicate email/phone)

