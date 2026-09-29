'use strict';


/*
 * =========================================
 * XAUUSD CHART
 * =========================================
 */

document.addEventListener('DOMContentLoaded', () => {

    const chartElement =
        document.getElementById('xauusd-chart');

    const dataElement =
        document.getElementById('chart-data');

    if (!chartElement || !dataElement) {
        return;
    }


    /*
     * =====================================
     * LOAD REAL M1 DATA
     * =====================================
     */

    let m1Data;

    try {

        m1Data =
            JSON.parse(
                dataElement.textContent
            );

    } catch (error) {

        console.error(
            'Failed to parse chart data:',
            error
        );

        return;
    }


    if (
        !Array.isArray(m1Data) ||
        m1Data.length === 0
    ) {

        console.warn(
            'No chart data available.'
        );

        return;
    }


    if (
        typeof LightweightCharts === 'undefined'
    ) {

        console.error(
            'LightweightCharts is not available.'
        );

        return;
    }


    /*
     * =====================================
     * SORT M1 DATA
     * =====================================
     */

    m1Data =
        [...m1Data].sort(
            (a, b) => a.time - b.time
        );


    /*
     * =====================================
     * AGGREGATE M1 -> HIGHER TIMEFRAME
     * =====================================
     *
     * M5  = 5-minute candles
     * M15 = 15-minute candles
     *
     * Aggregation uses real timestamp
     * boundaries, not array positions.
     * =====================================
     */

    function aggregateCandles(
        candles,
        minutes
    ) {

        const interval =
            minutes * 60;

        const groups =
            new Map();


        candles.forEach(
            (candle) => {

                const timestamp =
                    Number(candle.time);

                if (!Number.isFinite(timestamp)) {
                    return;
                }


                const bucket =
                    Math.floor(
                        timestamp / interval
                    ) * interval;


                if (!groups.has(bucket)) {

                    groups.set(
                        bucket,
                        {
                            time: bucket,
                            open: Number(candle.open),
                            high: Number(candle.high),
                            low: Number(candle.low),
                            close: Number(candle.close),

                            tick_volume:
                                Number(
                                    candle.tick_volume || 0
                                ),

                            real_volume:
                                Number(
                                    candle.real_volume || 0
                                ),

                            spread:
                                Number(
                                    candle.spread || 0
                                ),

                            count: 1
                        }
                    );

                    return;
                }


                const current =
                    groups.get(bucket);


                current.high =
                    Math.max(
                        current.high,
                        Number(candle.high)
                    );


                current.low =
                    Math.min(
                        current.low,
                        Number(candle.low)
                    );


                current.close =
                    Number(candle.close);


                current.tick_volume +=
                    Number(
                        candle.tick_volume || 0
                    );


                current.real_volume +=
                    Number(
                        candle.real_volume || 0
                    );


                current.spread =
                    Number(candle.spread || 0);


                current.count += 1;

            }
        );


        return Array.from(
            groups.values()
        )
        .sort(
            (a, b) => a.time - b.time
        )
        .map(
            (candle) => ({
                time: candle.time,
                open: candle.open,
                high: candle.high,
                low: candle.low,
                close: candle.close
            })
        );

    }


    /*
     * =====================================
     * BUILD TIMEFRAME DATA
     * =====================================
     */

    const timeframeData = {

        M1: m1Data,

        M5:
            aggregateCandles(
                m1Data,
                5
            ),

        M15:
            aggregateCandles(
                m1Data,
                15
            )

    };


    /*
     * =====================================
     * CREATE CHART
     * =====================================
     */

    const chart =
        LightweightCharts.createChart(
            chartElement,
            {
                width:
                    chartElement.clientWidth || 800,

                height:
                    chartElement.clientHeight || 405,

                layout: {
                    background: {
                        color: '#111827',
                    },

                    textColor: '#9ca3af',
                },

                grid: {
                    vertLines: {
                        color: '#1f2937',
                    },

                    horzLines: {
                        color: '#1f2937',
                    },
                },

                rightPriceScale: {
                    borderColor: '#374151',
                },

                timeScale: {
                    borderColor: '#374151',

                    timeVisible: true,

                    secondsVisible: false,
                },
            }
        );


    /*
     * =====================================
     * CANDLE SERIES
     * =====================================
     */

    const candleSeries =
        chart.addSeries(
            LightweightCharts.CandlestickSeries,
            {
                upColor: '#22c55e',

                downColor: '#ef4444',

                borderUpColor: '#22c55e',

                borderDownColor: '#ef4444',

                wickUpColor: '#22c55e',

                wickDownColor: '#ef4444',
            }
        );


    /*
     * =====================================
     * SET TIMEFRAME
     * =====================================
     */

    function setTimeframe(
        timeframe
    ) {

        const data =
            timeframeData[timeframe];


        if (
            !Array.isArray(data) ||
            data.length === 0
        ) {

            console.warn(
                'No data available for',
                timeframe
            );

            return;

        }


        candleSeries.setData(data);

        chart.timeScale().fitContent();


        showTimeframeStatus(
            timeframe,
            true,
            data.length
        );

    }


    /*
     * =====================================
     * TIMEFRAME STATUS
     * =====================================
     */

    function showTimeframeStatus(
        timeframe,
        available,
        count
    ) {

        const statusElement =
            document.getElementById(
                'timeframe-status'
            );


        if (!statusElement) {
            return;
        }


        if (available) {

            statusElement.textContent =
                timeframe
                + ' • LIVE DATA • '
                + count
                + ' candles';


            statusElement.removeAttribute(
                'data-unavailable'
            );


            return;
        }


        statusElement.textContent =
            timeframe
            + ' • DATA UNAVAILABLE';


        statusElement.setAttribute(
            'data-unavailable',
            'true'
        );

    }


    /*
     * =====================================
     * INITIAL TIMEFRAME
     * =====================================
     */

    setTimeframe('M1');


    /*
     * =====================================
     * TIMEFRAME BUTTONS
     * =====================================
     */

    const timeframeButtons =
        document.querySelectorAll(
            '.timeframe'
        );


    timeframeButtons.forEach(
        (button) => {

            button.addEventListener(
                'click',
                () => {

                    const timeframe =
                        button.dataset.timeframe;


                    if (
                        !timeframeData[
                            timeframe
                        ]
                    ) {

                        showTimeframeStatus(
                            timeframe,
                            false,
                            0
                        );

                        return;

                    }


                    timeframeButtons.forEach(
                        (item) => {

                            item.classList.remove(
                                'active'
                            );

                        }
                    );


                    button.classList.add(
                        'active'
                    );


                    setTimeframe(
                        timeframe
                    );

                }
            );

        }
    );


    /*
     * =====================================
     * CHART RESIZE
     * =====================================
     */

    window.addEventListener(
        'resize',
        () => {

            chart.applyOptions({

                width:
                    chartElement.clientWidth || 800,

                height:
                    chartElement.clientHeight || 405

            });

        }
    );

});


/*
 * =========================================
 * LIVE CLOCK
 * =========================================
 */

(function () {

    const liveTime =
        document.getElementById(
            'liveTime'
        );


    if (!liveTime) {
        return;
    }


    function updateClock() {

        const now =
            new Date();


        const hours =
            String(
                now.getHours()
            ).padStart(2, '0');


        const minutes =
            String(
                now.getMinutes()
            ).padStart(2, '0');


        const seconds =
            String(
                now.getSeconds()
            ).padStart(2, '0');


        liveTime.textContent =
            hours
            + ':'
            + minutes
            + ':'
            + seconds;

    }


    updateClock();


    setInterval(
        updateClock,
        1000
    );

})();


/*
 * =========================================
 * TRADING SESSIONS LIVE CLOCK
 * =========================================
 */

(function () {

    const clock =
        document.getElementById(
            'sessions-live-time'
        );


    const marker =
        document.getElementById(
            'sessions-current-time'
        );


    if (!clock || !marker) {
        return;
    }


    const timezone =
        clock.dataset.timezone;


    if (!timezone) {
        return;
    }


    function updateSessionsClock() {

        const now =
            new Date();


        const parts =
            new Intl.DateTimeFormat(
                'en-GB',
                {
                    timeZone:
                        timezone,

                    hour:
                        '2-digit',

                    minute:
                        '2-digit',

                    second:
                        '2-digit',

                    hourCycle:
                        'h23'
                }
            ).formatToParts(now);


        let hour = 0;
        let minute = 0;
        let second = 0;


        parts.forEach(
            (part) => {

                if (
                    part.type === 'hour'
                ) {

                    hour =
                        Number(
                            part.value
                        );

                }


                if (
                    part.type === 'minute'
                ) {

                    minute =
                        Number(
                            part.value
                        );

                }


                if (
                    part.type === 'second'
                ) {

                    second =
                        Number(
                            part.value
                        );

                }

            }
        );


        clock.textContent =
            String(hour).padStart(2, '0')
            + ':'
            + String(minute).padStart(2, '0')
            + ':'
            + String(second).padStart(2, '0');


        const totalMinutes =
            hour * 60
            + minute
            + second / 60;


        marker.style.left =
            (
                totalMinutes / 1440 * 100
            )
            + '%';

    }


    updateSessionsClock();


    setInterval(
        updateSessionsClock,
        1000
    );

})();


/*
 * =========================================
 * MODULE HOVER / IDENTIFICATION
 * =========================================
 */

(function () {

    const modules =
        document.querySelectorAll(
            '[data-slot]'
        );


    modules.forEach(
        (module) => {

            module.addEventListener(
                'mouseenter',
                () => {

                    module.dataset.hovered =
                        'true';

                }
            );


            module.addEventListener(
                'mouseleave',
                () => {

                    delete module.dataset.hovered;

                }
            );

        }
    );

})();
