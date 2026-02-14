// Test all Proxima providers with the same English question
const question = 'What are the top 3 advantages of TypeScript over JavaScript? Keep it brief, 2-3 sentences per point.';

async function testProvider(model) {
    try {
        const res = await fetch('http://localhost:3210/v1/chat/completions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model, message: question })
        });
        const data = await res.json();
        const content = data.choices?.[0]?.message?.content || '';
        const time = data.proxima?.responseTimeMs || 0;
        const ok = content !== 'No response captured' && content.length > 10;

        console.log(`--- ${model.toUpperCase()} ---`);
        console.log(`Status: ${ok ? 'OK' : 'FAILED'}`);
        console.log(`Time: ${time} ms`);
        console.log(`Length: ${content.length} chars`);
        console.log(`Content: ${content.substring(0, 400)}`);
        console.log('');
        return { model, ok, time, length: content.length, content };
    } catch (e) {
        console.log(`--- ${model.toUpperCase()} --- ERROR: ${e.message}`);
        return { model, ok: false, time: 0, length: 0, error: e.message };
    }
}

async function main() {
    console.log('=== Proxima Multi-AI English Test ===');
    console.log(`Question: ${question}`);
    console.log('');

    const results = [];
    for (const model of ['perplexity', 'chatgpt', 'gemini']) {
        results.push(await testProvider(model));
    }

    console.log('=== SUMMARY ===');
    for (const r of results) {
        console.log(`${r.model}: ${r.ok ? 'OK' : 'FAILED'} | ${r.time}ms | ${r.length} chars`);
    }
}

main();
