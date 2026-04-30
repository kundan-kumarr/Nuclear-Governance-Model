# Challenge 4: The Nuclear Governance Model

**Complexity:** Medium-High

## The Question

Do nuclear agreements follow a distinct "design template" compared to agreements governing other weapon categories? If so, what makes the nuclear model architecturally different?

## Why It Matters

Proposals for an "IAEA for AI" assume that nuclear governance is both distinctive and transferable. But is it? If nuclear agreements systematically differ from others in their verification profiles, inspector arrangements, or compliance mechanisms, that tells us something specific about what the nuclear model actually contains. And that matters for judging whether it can be transplanted to a fundamentally different technology domain.

## Your Task

Compare nuclear and non-nuclear agreements across multiple dimensions of governance design: compliance mechanism types, inspector arrangements, access provisions, and trigger mechanisms. Test whether differences are statistically significant and assess how large the effects are. Identify which specific design features are unique to the nuclear domain and which are shared with other weapon categories.

**Datasets to start with:** `agreement_info`, `vercom`, `weapons_facilities`

**Tip:** Use `summary_category` in `weapons_facilities` to create a nuclear/non-nuclear flag. Then compare groups across the compliance and verification variables in `agreement_info` and `vercom`.

## AI Governance Extension (Optional)

Which nuclear governance features could plausibly transfer to AI? Consider which features depend on nuclear-specific properties: physical inspectability (nuclear materials can be detected), geographic concentration (facilities are fixed), and state-centric development (governments run nuclear programs). AI differs on all three dimensions. What survives the translation?
