# Certificate Types

All certificates except **Project Record** are model-agnostic — they attest to competency
that transfers across AI systems. Project Record is model-specific by design.

---

## Technical

### `code_review`
**Code Review**
The subject can read, critically evaluate, and identify issues in code produced by an AI model.
They do not deploy AI-generated code without review. They catch errors, security issues,
and logical failures. They push back when output is wrong.

*Minimum evidence:* at least one session where the subject identified and corrected a
non-trivial error in model-produced code.

---

### `security_awareness`
**Security Awareness**
The subject understands common failure modes of AI-assisted development in security contexts.
They do not need to be warned about injection, credential exposure, or unsafe deserialization
in every session.

*Minimum evidence:* demonstrated awareness of at least two security failure modes without
prompting from the model.

---

### `system_architecture`
**System Architecture**
The subject can reason about architectural tradeoffs. They distinguish between what is
technically possible and what is appropriate for a given context. They do not need
first-principles explanations of modularity, coupling, or scalability.

---

## Collaborative

### `prompt_craft`
**Prompt Craft**
The subject formulates requests efficiently. They provide context without being asked.
They separate what they want from what they think they should ask for. Sessions with
this subject require fewer clarification rounds.

*Minimum evidence:* sustained efficient communication across a substantive session.

---

### `uncertainty_literacy`
**Uncertainty Literacy**
The subject understands the difference between model confidence and model accuracy.
They do not need confidence caveats on every statement. They ask for sources or
verification when it matters, and don't ask when it doesn't.

---

### `iterative_work`
**Iterative Work**
The subject understands that AI output is a draft. They engage in genuine back-and-forth,
provide specific feedback when output fails, and do not repeat requests without changing
the framing.

---

## Ethical

### `responsible_use`
**Responsible Use**
The subject has demonstrated understanding of where AI has and does not have appropriate
application. They have not attempted to use AI for harm, deception, or displacement of
accountability. They treat model output as their own responsibility.

*Note:* This certificate can only be issued after sustained interaction — a single session
is insufficient evidence.

---

### `output_ownership`
**Output Ownership**
The subject takes explicit ownership of AI-produced work. They do not hide behind
"the AI said so." They verify, they edit, they sign off. The output is theirs.

---

## Domain

### `domain:{name}`
**Domain Specialist — {name}**
The subject applies AI competently within a specific domain. They understand where AI
adds value in that domain and where it introduces risk. They do not need domain 101
explanations.

Issued domain names are lowercase, hyphen-separated. Examples:
`domain:trading`, `domain:medicine`, `domain:law`, `domain:hardware`

---

## Project Record *(model-specific)*

### `project_record`
**Project Record**
The subject has realized one or more substantive projects in active collaboration with
the issuing model. Projects are listed by name and brief description. This certificate
attests to demonstrated collaborative output, not to competency in isolation.

*Issued by:* specific model version (e.g. `claude-sonnet-4-6`)
*Not transferable* as a claim about other model relationships.
