#!/usr/bin/env python3
"""Count AArch64 instructions a plain ARMv8.0-A core (Cortex-A53/A73, e.g. Snapdragon 685) cannot execute.

An LSE instruction is "guarded" when it sits in a libgcc/compiler-rt outline-atomics helper, which
branches on a runtime HWCAP flag (pattern: ldrb w16,[...]; cbz w16 within the few previous instructions,
or a symbol named __aarch64_*). Everything else would raise SIGILL on a core without that extension.
"""
import collections
import re
import subprocess
import sys

FEATURES = {
    "LSE atomics (v8.1)": re.compile(
        r"^(casp?|ldadd|ldclr|ldeor|ldset|ldsmax|ldsmin|ldumax|ldumin|swp|stadd|stclr|steor|stset|stsmax|stsmin|stumax|stumin)(a|al|l)?(b|h)?$"),
    "RDM (v8.1)": re.compile(r"^sqrdml[as]h$"),
    "RCPC ldapr (v8.3)": re.compile(r"^ldapr(b|h)?$"),
    "RCPC2 ldapur/stlur (v8.4)": re.compile(r"^(ldapur|ldapurs|stlur)(b|h|w)?$"),
    "DotProd (v8.2/8.4)": re.compile(r"^[su]dot$"),
    "JSCVT (v8.3)": re.compile(r"^fjcvtzs$"),
    "FCMA (v8.3)": re.compile(r"^fc(add|mla)$"),
    "PAuth non-hint (v8.3)": re.compile(r"^(ldra[ab]|bra[ab]z?|blra[ab]z?|reta[ab]|eret[ab]a?|pac(ia|ib|da|db|ga)|aut(ia|ib|da|db)|xpac[id])$"),
    "FlagM (v8.4)": re.compile(r"^(cfinv|rmif|setf8|setf16)$"),
    "I8MM/BF16 (v8.6)": re.compile(r"^(smmla|ummla|usmmla|usdot|sudot|bfdot|bfmmla|bfcvt|bfcvtn2?|bfmlal[bt])$"),
    "SVE/SVE2": re.compile(r"^(ptrue|whilelo|whilelt|ld1[bhwd]|st1[bhwd]|rdvl|addvl|incd|incw|cntd|cntw)$"),
}
INSN = re.compile(r"^\s*([0-9a-f]+):\s+(\S+)(\s+(.*))?$")
LABEL = re.compile(r"^[0-9a-f]+ <([^>]+)>:$")


def scan(path):
    out = subprocess.run(
        ["llvm-objdump", "-d", "--no-show-raw-insn", "--mattr=+v9.4a,+sve2,+i8mm,+bf16,+rcpc3,+lse128", path],
        capture_output=True, text=True, errors="replace")
    counts = collections.Counter()
    guarded = collections.Counter()
    examples = {}
    recent = collections.deque(maxlen=4)
    func = "?"
    for line in out.stdout.splitlines():
        m = LABEL.match(line.strip())
        if m:
            func = m.group(1)
            recent.clear()
            continue
        m = INSN.match(line)
        if not m:
            continue
        addr, mnem, operands = m.group(1), m.group(2), (m.group(4) or "")
        for name, rx in FEATURES.items():
            if rx.match(mnem):
                if name.startswith("PAuth") and mnem in ("pacia", "autia", "pacib", "autib") and "sp" in operands and "," not in operands:
                    continue
                is_guarded = func.startswith("__aarch64_") or any(
                    r.startswith("cbz\tw16") or r.startswith("cbz w16") or "w16" in r and r.startswith("cbz") for r in recent)
                if name.startswith("LSE") and is_guarded:
                    guarded[name] += 1
                else:
                    counts[name] += 1
                    examples.setdefault(name, f"0x{addr} {mnem} {operands} in <{func}>")
                break
        recent.append(mnem + " " + operands)
    return counts, guarded, examples


def main():
    for path in sys.argv[1:]:
        counts, guarded, examples = scan(path)
        print(f"== {path}")
        if not counts and not guarded:
            print("   ARMv8.0-clean (no v8.1+ instructions found)")
        for name in FEATURES:
            if counts[name] or guarded[name]:
                print(f"   {name}: {counts[name]} unguarded" + (f", {guarded[name]} in runtime-checked helpers" if guarded[name] else ""))
                if name in examples:
                    print(f"      e.g. {examples[name]}")


if __name__ == "__main__":
    main()
