Yes—it's absolutely right to say that **Lychee is focused on service-oriented monorepos**, not library/package monorepos.

---

## 🧠 Why Lychee Is Service-Centric

Lychee’s architecture and feature set are designed around the orchestration of **independent services** that:

- Communicate via **contracts** (schemas)
- Are written in **different languages** (polyglot)
- Have **lifecycles** (start, stop, health check)
- Require **hot reloading**, **log aggregation**, and **dependency graphs**

This aligns with the needs of **microservice-style monorepos**, where each unit is a deployable service—not just a reusable library.

---

## 🧱 What Lychee Is Not (By Design)

It’s **not** optimized for:

- Managing shared libraries across packages
- Publishing versioned packages to registries (like PyPI or npm)
- Handling semantic versioning, changelogs, or dependency resolution between internal libs

Those are concerns typically handled by tools like:

- **Lerna** (for JS monorepos)
- **Poetry workspaces** or **Hatch** (for Python libs)
- **Nx** (for mixed frontend/backend libs)

---

## 🧩 Why This Matters

This distinction affects how you:

- **Model your domain**: services have contracts and lifecycles; libraries have APIs and versions
- **Design your CLI**: `lx dev` starts services, not builds packages
- **Implement primitives**: queues, hooks, and schema sync make sense for services, not for libs

---

## 🛠️ Can Lychee Support Libs Eventually?

Sure—if you extend it. You could imagine a future where Lychee supports:

- Internal package linking
- Type-safe shared models across services
- Versioned schema modules

But that would require a shift in its core philosophy—from **contract-first orchestration** to **package-first composition**.

---

So yes, Lychee is purpose-built for **service monorepos**—and that’s what makes it powerful.
