<template>
    <div class="page-container">
        <header>
            <h3>velotag</h3>
        </header>

        <main class="page-content">
            <div class="coming-soon-card">
                <div class="icon-box">
                    <svg xmlns="http://www.w3.org/2000/svg" height="32px" viewBox="0 -960 960 960" width="32px">
                        <path d="M480-80q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Zm28 168-20-172-140-84 160 56 160-56-140 84-20 172Z"/>
                        <path d="M454-160v-84q-101-9-170.5-75T204-484h84q9 77 69 130.5T480-300q84 0 143-56.5T684-492q0-80-53-137t-131-69v-84q114 14 187 100t73 202q0 122-79.5 208T454-160Z"/>
                    </svg>
                </div>

                <h1>Coming Soon</h1>
                <p class="subtitle">Diese Seite ist noch in Arbeit.</p>
                <p class="joke">
                    Wir sind quasi rund um die Uhr am Coden — außer wenn der Kaffee leer ist.
                    Dann dauert's noch ein bisschen. ☕
                </p>

                <div class="progress-bar-wrap">
                    <div class="progress-bar"></div>
                </div>
                <span class="progress-label">Irgendwo zwischen "fast fertig" und "fangen wir nochmal von vorne an"</span>
            </div>
        </main>
    </div>
</template>

<style scoped>
    .page-container {
        min-height: 100vh;
        background-color: #f8f9fa;
        display: flex;
        flex-direction: column;
    }

    header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        background-color: #ffffff;
        box-shadow: 0 0.2rem 0.6rem rgba(0, 0, 0, 0.05);
        box-sizing: border-box;
        padding: 1.2rem 2rem;
        min-height: 4.8rem;
    }
    header h3 {
        font-size: 1.25rem;
        font-weight: 500;
        margin: 0;
        padding-left: calc(2.5rem + 88px);
        color: #2c3e50;
    }

    .page-content {
        flex: 1;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 3rem 2rem;
        box-sizing: border-box;
    }

    .coming-soon-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1.2rem;
        background-color: #ffffff;
        padding: 3rem 2.5rem;
        border-radius: 1rem;
        box-shadow: 0 0.4rem 1.2rem rgba(0, 0, 0, 0.05);
        border: 2px solid transparent;
        max-width: 32rem;
        width: 100%;
        text-align: center;
    }

    .icon-box {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 4.5rem;
        height: 4.5rem;
        background-color: #e8f7f3;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .icon-box svg {
        fill: #3db897;
    }

    h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
    }

    .subtitle {
        margin: 0;
        font-size: 1rem;
        color: #7f8c8d;
    }

    .joke {
        margin: 0;
        font-size: 0.95rem;
        color: #64748b;
        line-height: 1.6;
        background-color: #f8fafc;
        border-radius: 0.6rem;
        padding: 0.8rem 1rem;
        border-left: 3px solid #3db897;
    }

    .progress-bar-wrap {
        width: 100%;
        height: 0.5rem;
        background-color: #e2e8f0;
        border-radius: 999px;
        overflow: hidden;
        margin-top: 0.4rem;
    }

    .progress-bar {
        height: 100%;
        width: 62%;
        background: linear-gradient(90deg, #3db897, #2da081);
        border-radius: 999px;
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }

    .progress-label {
        font-size: 0.78rem;
        color: #94a3b8;
        font-style: italic;
    }
</style>
