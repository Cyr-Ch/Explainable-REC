"""
Dataset generation script

Generates test questions for evaluation across different categories.
Run with: python scripts/pipelines/dataset_generation/build_dataset.py --out questions.jsonl --n 60
"""

import argparse, json, random

TEMPLATES = {
    'QPimpPexp': [
        'What happens if imports increase by {pct}%?',
        'Reduce exports by {pct}%. What is the new cost?',
        'If exports rise by {pct}%, how does the profit change?',
        'Assume imports decrease by {pct}%. Compute the objective.'
    ],
    'QPconsPprod': [
        'Increase PV generation by {pct}%. How does the objective change?',
        'Increase consumption by {pct}%. What is the outcome?',
        'Decrease load by {pct}% during the day. Evaluate the impact.'
    ],
    'QPshift': [
        'What if we shift {pct}% of the load from {h1} to {h2}?',
        'Shift {pct}% from hour {h1} to {h2} and report the cost.'
    ]
}

def sample(cat):
    """Sample a question from a category"""
    if cat == 'QPimpPexp':
        return random.choice(TEMPLATES[cat]).format(
            pct=random.choice([5, 10, 15, 20, -5, -10, -15, -20])
        )
    if cat == 'QPconsPprod':
        return random.choice(TEMPLATES[cat]).format(
            pct=random.choice([5, 10, 20, 25, -10, -20])
        )
    if cat == 'QPshift':
        pct = random.choice([25, 33, 50, 67, 75])
        h1 = random.choice([7, 8, 9, 10, 12, 13, 17, 18, 20])
        h2 = random.choice([6, 11, 14, 15, 16, 19, 21, 22, 23])
        if h1 == h2:
            h2 = (h2 + 1) % 24
        return random.choice(TEMPLATES[cat]).format(pct=pct, h1=h1, h2=h2)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Generate test questions for evaluation')
    ap.add_argument('--out', required=True, help='Output file path')
    ap.add_argument('--n', type=int, default=60, help='Number of questions to generate')
    args = ap.parse_args()
    
    random.seed(1337)
    cats = list(TEMPLATES.keys())
    
    with open(args.out, 'w', encoding='utf-8') as f:
        for _ in range(args.n):
            q = sample(random.choice(cats))
            f.write(json.dumps({'question': q}) + '\n')
    
    print(f'Wrote {args.n} questions to {args.out}')

