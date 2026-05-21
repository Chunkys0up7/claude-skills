# The refactor menu

Worked examples of the standard moves. When `SKILL.md` flags something, this is the playbook.

The names are from Fowler's *Refactoring*. The examples are language-agnostic but lean on Python
and TypeScript for readability.

---

## Extract Function

**When**: a chunk of code inside a longer function has a single purpose and you can name what it
does in a short phrase.

**Before:**
```python
def ship_orders():
    orders = fetch_orders()
    for order in orders:
        # compute tax-inclusive total
        total = 0
        for item in order.items:
            total += item.price * 1.08
        order.total = total
        send_to_carrier(order)
```

**After:**
```python
def ship_orders():
    for order in fetch_orders():
        order.total = tax_inclusive_total(order.items)
        send_to_carrier(order)

def tax_inclusive_total(items: list[Item]) -> Money:
    """Total with 8% sales tax included."""
    return sum(item.price * TAX_MULTIPLIER for item in items)
```

The orchestrator now reads as a story; the arithmetic has a name.

---

## Extract Class

**When**: a class has fields and methods that cluster around a sub-concept of its job — and that
sub-concept could stand on its own.

**Before:** `Order` has fields `street`, `city`, `postal_code`, `country` and methods
`validate_address()`, `format_address()`.

**After:** extract `Address` as its own class; `Order` has an `address: Address` field.

**Heuristic**: if you can name a tuple of fields with a noun ("the customer's *address*"), it's
probably its own class.

---

## Extract Module

**When**: a file has multiple unrelated classes/functions, or a single file grows past ~400 LOC.

**Before**: `models.py` contains `User`, `Order`, `Product`, `Invoice`, `Subscription`, all
mashed together.

**After**: `models/user.py`, `models/order.py`, `models/product.py`, ... and `models/__init__.py`
re-exports the public surface.

---

## Inline Function (the reverse)

**When**: a function adds no clarity beyond its name — its body is as readable as its call site,
or it's the only caller.

**Before:**
```python
def is_active(user):
    return user.status == "active"

# only one caller
if is_active(user):
    ...
```

**After:**
```python
if user.status == ACTIVE_STATUS:
    ...
```

(But: if `is_active` is *named documentation*, keep it. The question is whether the abstraction
earns its keep.)

---

## Introduce Parameter Object

**When**: a function has 5+ parameters or several params travel together to multiple functions.

**Before:**
```python
def create_user(name, email, age, country, plan, referrer, signup_source):
    ...
```

**After:**
```python
@dataclass(frozen=True)
class UserSignup:
    name: str
    email: str
    age: int
    country: str
    plan: PlanTier
    referrer: str | None
    signup_source: SignupSource

def create_user(signup: UserSignup) -> User:
    ...
```

Bonus: the dataclass becomes a place to validate and a thing to log.

---

## Replace Boolean Parameter with Enum (or split functions)

**Before:**
```python
def export_report(data, as_pdf, include_charts, redact_pii):
    ...

# call site — impossible to read
export_report(data, True, False, True)
```

**After (enum):**
```python
class ExportFormat(Enum):
    PDF = "pdf"
    HTML = "html"

@dataclass(frozen=True)
class ExportOptions:
    format: ExportFormat
    include_charts: bool = True
    redact_pii: bool = False

export_report(data, ExportOptions(format=ExportFormat.PDF, redact_pii=True))
```

**Or split:**
```python
def export_pdf(data, *, include_charts: bool = True, redact_pii: bool = False): ...
def export_html(data, *, include_charts: bool = True, redact_pii: bool = False): ...
```

Splitting is best when the two branches don't share much code.

---

## Guard Clauses (replace nested conditionals)

**Before:**
```python
def process(user):
    if user is not None:
        if user.active:
            if user.subscription is not None:
                if user.subscription.valid:
                    do_the_thing(user)
```

**After:**
```python
def process(user):
    if user is None: return
    if not user.active: return
    if user.subscription is None: return
    if not user.subscription.valid: return
    do_the_thing(user)
```

The happy path is at the bottom; the rejections are an obvious list above.

---

## Replace Conditional with Polymorphism (or lookup table)

**Before:**
```python
def area(shape):
    if shape.kind == "circle":
        return math.pi * shape.radius ** 2
    elif shape.kind == "rect":
        return shape.w * shape.h
    elif shape.kind == "triangle":
        return shape.base * shape.height / 2
```

**After (polymorphism):**
```python
class Shape(Protocol):
    def area(self) -> float: ...

class Circle:
    def __init__(self, r: float): self.r = r
    def area(self) -> float: return math.pi * self.r ** 2

class Rect:
    def __init__(self, w: float, h: float): self.w, self.h = w, h
    def area(self) -> float: return self.w * self.h
```

**Or (lookup table)** — better when behavior is data, not code:
```python
HANDLERS = {
    "ping": handle_ping,
    "pong": handle_pong,
    "fin":  handle_fin,
}
HANDLERS[msg.kind](msg)
```

Don't reach for polymorphism on every conditional — sometimes an `if`/`elif` chain is just
clearer. Polymorphism pays off when the branches need their own state or evolve independently.

---

## Introduce Named Constant

**Before:**
```python
if retries < 5:
    time.sleep(0.250 * (2 ** retries))
```

**After:**
```python
MAX_RETRIES: Final = 5
BASE_BACKOFF_SECONDS: Final = 0.250  # matches upstream timeout floor

if retries < MAX_RETRIES:
    time.sleep(BASE_BACKOFF_SECONDS * (2 ** retries))
```

The comment explains the *why* — that's the value-add over the original.

---

## Move Function / Move Field

**When**: a method on class `A` uses more of class `B`'s data than its own, or a field belongs
conceptually to a different class.

**Heuristic**: "feature envy" — if `A.compute_x()` calls `b.foo`, `b.bar`, `b.baz`, the method
wants to live on `B`.

---

## Replace Inheritance with Composition

**When**: an inheritance chain is being used for code reuse rather than genuine "is-a" semantics.

**Before:**
```python
class TimestampedThing:
    def __init__(self):
        self.created_at = now()

class LoggedThing(TimestampedThing):
    def log(self, msg): ...

class User(LoggedThing):
    ...
```

**After:**
```python
@dataclass
class Timestamps:
    created_at: datetime = field(default_factory=now)

class Logger:
    def log(self, msg): ...

@dataclass
class User:
    timestamps: Timestamps
    logger: Logger
    ...
```

Composition makes the dependencies explicit; inheritance hides them in the MRO.

---

## Collapse Hierarchy (over-abstraction → less abstraction)

**When**: a base class has one subclass and that's been true for a year; or an interface has one
implementation forever.

**Move**: merge them. Add the abstraction back the day you need a second variant.

---

## Replace Loop with Pipeline

**Before:**
```python
result = []
for order in orders:
    if order.status == "paid":
        result.append(order.total)
total = sum(result)
```

**After:**
```python
total = sum(o.total for o in orders if o.status == "paid")
```

This is good *up to about two operations*. A 5-stage chained pipeline can be harder to read than
a named loop. Use judgment.

---

## When NOT to refactor

- **You're about to delete the code anyway.** No point polishing.
- **The "after" is more abstract but no shorter or clearer.** You're adding indirection without
  paying for it.
- **You don't have test coverage for the area.** Refactor without a safety net is risky; add a
  test first.
- **The user said "just hack it in".** Note the debt, mention it once, then defer.
