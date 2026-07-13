// =============================================
// REPORTS DASHBOARD
// =============================================

document.addEventListener("DOMContentLoaded", function () {

    initializeCharts();

    animateStatistics();

    initializeDateFilter();

    initializeExportButtons();

});


// =============================================
// ANIMATE NUMBERS
// =============================================

function animateStatistics() {

    const numbers = document.querySelectorAll(".stat-number");

    numbers.forEach(number => {

        const target = parseInt(number.dataset.value);

        if (isNaN(target)) return;

        let current = 0;

        const increment = Math.ceil(target / 60);

        const timer = setInterval(() => {

            current += increment;

            if (current >= target) {

                current = target;

                clearInterval(timer);

            }

            number.innerText = current.toLocaleString();

        }, 20);

    });

}


// =============================================
// CHARTS
// =============================================

function initializeCharts() {

    if (typeof Chart === "undefined") {

        console.log("Chart.js not loaded");

        return;

    }

    // =====================================
    // USERS CHART
    // =====================================

    const usersCanvas = document.getElementById("usersChart");

    if (usersCanvas) {

        new Chart(usersCanvas, {

            type: "bar",

            data: {

                labels: chartData.months,

                datasets: [

                    {

                        label: "New Users",

                        data: chartData.users,

                        backgroundColor: "#7C3AED",

                        borderRadius: 8

                    }

                ]

            },

            options: {

                responsive: true,

                plugins: {

                    legend: {

                        display: false

                    }

                }

            }

        });

    }

    // =====================================
    // CHAT CHART
    // =====================================

    const chatCanvas = document.getElementById("chatChart");

    if (chatCanvas) {

        new Chart(chatCanvas, {

            type: "line",

            data: {

                labels: chartData.months,

                datasets: [

                    {

                        label: "AI Conversations",

                        data: chartData.chats,

                        borderColor: "#EC4899",

                        backgroundColor: "rgba(236,72,153,.15)",

                        fill: true,

                        tension: 0.4

                    }

                ]

            },

            options: {

                responsive: true

            }

        });

    }

    // =====================================
    // REMINDERS PIE
    // =====================================

    const reminderCanvas = document.getElementById("reminderChart");

    if (reminderCanvas) {

        new Chart(reminderCanvas, {

            type: "doughnut",

            data: {

                labels: [

                    "Completed",

                    "Upcoming",

                    "Missed"

                ],

                datasets: [

                    {

                        data: [

                            chartData.completed,

                            chartData.upcoming,

                            chartData.missed

                        ],

                        backgroundColor: [

                            "#10B981",

                            "#7C3AED",

                            "#EF4444"

                        ]

                    }

                ]

            },

            options: {

                responsive: true

            }

        });

    }

}


// =============================================
// DATE FILTER
// =============================================

function initializeDateFilter() {

    const filter = document.getElementById("reportRange");

    if (!filter) return;

    filter.addEventListener("change", function () {

        window.location.href =
            "?range=" + this.value;

    });

}


// =============================================
// CSV EXPORT
// =============================================

function initializeExportButtons() {

    const csv = document.getElementById("exportCSV");

    if (csv) {

        csv.addEventListener("click", function () {

            window.location.href =
                "/admin/reports/export/csv";

        });

    }

    const pdf = document.getElementById("exportPDF");

    if (pdf) {

        pdf.addEventListener("click", function () {

            window.location.href =
                "/admin/reports/export/pdf";

        });

    }

    const refresh = document.getElementById("refreshReports");

    if (refresh) {

        refresh.addEventListener("click", function () {

            location.reload();

        });

    }

}


// =============================================
// PRINT REPORT
// =============================================

function printReport() {

    window.print();

}


// =============================================
// DOWNLOAD IMAGE OF CHART
// =============================================

function downloadChart(chartId, filename) {

    const canvas = document.getElementById(chartId);

    if (!canvas) return;

    const link = document.createElement("a");

    link.download = filename;

    link.href = canvas.toDataURL("image/png");

    link.click();

}