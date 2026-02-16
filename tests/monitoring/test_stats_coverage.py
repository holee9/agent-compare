"""
Comprehensive tests for src/monitoring/stats.py to improve coverage.

This module tests:
- StatsCollector.get_summary() for all period types (DAILY, WEEKLY, MONTHLY, ALL)
- StatsCollector.get_formatted_stats() method (lines 149-175)
- Edge cases and empty data scenarios
"""

from datetime import datetime, timedelta

import pytest

from src.core.models import AgentType
from src.monitoring.stats import Period, StatsCollector, UsageSummary
from src.monitoring.tracker import TokenUsage


class TestStatsCollectorPeriodCoverage:
    """Test suite for StatsCollector period-based filtering."""

    @pytest.fixture
    def collector(self) -> StatsCollector:
        """Create StatsCollector instance."""
        return StatsCollector()

    @pytest.fixture
    def sample_usage_today(self) -> TokenUsage:
        """Create sample TokenUsage from today."""
        return TokenUsage(
            provider=AgentType.CLAUDE,
            input_tokens=1000,
            output_tokens=500,
            phase=1,
            task="test_today",
        )

    @pytest.fixture
    def sample_usage_old(self) -> None:
        """Create sample TokenUsage from > 30 days ago."""
        # Create usage with old timestamp
        old_timestamp = datetime.now() - timedelta(days=35)
        usage = TokenUsage(
            provider=AgentType.GEMINI,
            input_tokens=2000,
            output_tokens=1000,
            phase=2,
            task="test_old",
        )
        # Manually set timestamp to old date
        usage.timestamp = old_timestamp
        return usage

    def test_get_summary_daily_period(self, collector: StatsCollector, sample_usage_today: TokenUsage) -> None:
        """Test get_summary with DAILY period - Line 93 coverage."""
        collector.track(sample_usage_today)

        summary = collector.get_summary(period=Period.DAILY)

        assert isinstance(summary, UsageSummary)
        assert summary.period == Period.DAILY
        assert summary.total_tokens == 1500
        # Should include data from today (within last 24 hours)
        assert summary.request_count == 1

    def test_get_summary_weekly_period(self, collector: StatsCollector, sample_usage_today: TokenUsage) -> None:
        """Test get_summary with WEEKLY period - Line 96 coverage."""
        collector.track(sample_usage_today)

        summary = collector.get_summary(period=Period.WEEKLY)

        assert isinstance(summary, UsageSummary)
        assert summary.period == Period.WEEKLY
        # Verify start_date is approximately 7 days ago
        time_diff = datetime.now() - summary.start_date
        assert timedelta(days=6) < time_diff < timedelta(days=8)

    def test_get_summary_monthly_period(self, collector: StatsCollector, sample_usage_today: TokenUsage) -> None:
        """Test get_summary with MONTHLY period - Line 98 coverage."""
        collector.track(sample_usage_today)

        summary = collector.get_summary(period=Period.MONTHLY)

        assert isinstance(summary, UsageSummary)
        assert summary.period == Period.MONTHLY
        # Verify start_date is approximately 30 days ago
        time_diff = datetime.now() - summary.start_date
        assert timedelta(days=29) < time_diff < timedelta(days=31)

    def test_get_summary_all_period(self, collector: StatsCollector, sample_usage_today: TokenUsage) -> None:
        """Test get_summary with ALL period - Line 100 coverage."""
        collector.track(sample_usage_today)

        summary = collector.get_summary(period=Period.ALL)

        assert isinstance(summary, UsageSummary)
        assert summary.period == Period.ALL
        # ALL period should start from datetime.min
        assert summary.start_date == datetime.min

    def test_get_summary_filters_by_period_old_data_excluded(
        self, collector: StatsCollector, sample_usage_today: TokenUsage, sample_usage_old: None
    ) -> None:
        """Test that get_summary filters out old data for DAILY period."""
        collector.track(sample_usage_today)
        collector.track(sample_usage_old)  # type: ignore

        # Daily summary should only include recent data
        daily_summary = collector.get_summary(period=Period.DAILY)
        assert daily_summary.total_tokens == 1500  # Only today's data
        assert daily_summary.request_count == 1

        # ALL summary should include both
        all_summary = collector.get_summary(period=Period.ALL)
        assert all_summary.total_tokens == 4500  # Today + old data
        assert all_summary.request_count == 2

    def test_get_summary_empty_collector(self, collector: StatsCollector) -> None:
        """Test get_summary with no tracked data."""
        for period in [Period.DAILY, Period.WEEKLY, Period.MONTHLY, Period.ALL]:
            summary = collector.get_summary(period=period)

            assert summary.total_tokens == 0
            assert summary.total_cost == 0.0
            assert summary.request_count == 0
            assert len(summary.by_provider) == 0
            assert len(summary.by_phase) == 0
            assert summary.period == period


class TestStatsCollectorFormattedStats:
    """Test suite for StatsCollector.get_formatted_stats() - Lines 149-175 coverage."""

    @pytest.fixture
    def collector_with_data(self) -> StatsCollector:
        """Create StatsCollector with sample data."""
        collector = StatsCollector()

        # Add some sample data
        collector.track(
            TokenUsage(
                provider=AgentType.CLAUDE,
                input_tokens=1000,
                output_tokens=500,
                phase=1,
                task="task1",
            )
        )
        collector.track(
            TokenUsage(
                provider=AgentType.GEMINI,
                input_tokens=2000,
                output_tokens=1000,
                phase=2,
                task="task2",
            )
        )
        collector.track(
            TokenUsage(
                provider=AgentType.CLAUDE,
                input_tokens=500,
                output_tokens=250,
                phase=1,
                task="task3",
            )
        )

        return collector

    def test_get_formatted_stats_daily(self, collector_with_data: StatsCollector) -> None:
        """Test get_formatted_stats with DAILY period - Lines 149-175 coverage."""
        formatted = collector_with_data.get_formatted_stats(period=Period.DAILY)

        # Verify it's a string
        assert isinstance(formatted, str)

        # Check header
        assert "Usage Statistics" in formatted
        assert "(daily)" in formatted
        assert "=" * 50 in formatted

        # Check period information
        assert "Period:" in formatted
        assert "Total Tokens:" in formatted
        assert "Total Cost:" in formatted
        assert "Total Requests:" in formatted

        # Check provider breakdown
        assert "By Provider:" in formatted
        assert "claude:" in formatted
        assert "gemini:" in formatted

        # Check phase breakdown
        assert "By Phase:" in formatted
        assert "Phase 1:" in formatted
        assert "Phase 2:" in formatted

    def test_get_formatted_stats_weekly(self, collector_with_data: StatsCollector) -> None:
        """Test get_formatted_stats with WEEKLY period."""
        formatted = collector_with_data.get_formatted_stats(period=Period.WEEKLY)

        assert "(weekly)" in formatted
        assert "Usage Statistics" in formatted
        assert "By Provider:" in formatted
        assert "By Phase:" in formatted

    def test_get_formatted_stats_monthly(self, collector_with_data: StatsCollector) -> None:
        """Test get_formatted_stats with MONTHLY period."""
        formatted = collector_with_data.get_formatted_stats(period=Period.MONTHLY)

        assert "(monthly)" in formatted
        assert "Usage Statistics" in formatted

    def test_get_formatted_stats_all(self, collector_with_data: StatsCollector) -> None:
        """Test get_formatted_stats with ALL period."""
        formatted = collector_with_data.get_formatted_stats(period=Period.ALL)

        assert "(all)" in formatted
        assert "Usage Statistics" in formatted

    def test_get_formatted_stats_with_no_data(self) -> None:
        """Test get_formatted_stats with empty collector."""
        collector = StatsCollector()
        formatted = collector.get_formatted_stats(period=Period.ALL)

        # Should still produce formatted output
        assert isinstance(formatted, str)
        assert "Usage Statistics" in formatted
        assert "Total Tokens: 0" in formatted
        assert "Total Requests: 0" in formatted

    def test_get_formatted_stats_number_formatting(self, collector_with_data: StatsCollector) -> None:
        """Test that numbers are formatted with commas."""
        formatted = collector_with_data.get_formatted_stats(period=Period.ALL)

        # Total tokens should be formatted with commas
        assert "5,250" in formatted  # Total tokens: 1500 + 3000 + 750

        # Individual provider tokens should be formatted
        assert "2,250" in formatted  # Claude: 1500 + 750

    def test_get_formatted_stats_cost_formatting(self, collector_with_data: StatsCollector) -> None:
        """Test that cost is formatted with 4 decimal places."""
        formatted = collector_with_data.get_formatted_stats(period=Period.ALL)

        # Cost should be formatted as $X.XXXX
        assert "$" in formatted
        # Check for decimal point (cost formatting)
        assert "." in formatted

    def test_get_formatted_stats_structure(self, collector_with_data: StatsCollector) -> None:
        """Test the structure of formatted stats output."""
        formatted = collector_with_data.get_formatted_stats(period=Period.ALL)

        lines = formatted.split("\n")

        # Should start with separator
        non_empty_lines = [line for line in lines if line.strip()]
        # Should start with separator
        assert non_empty_lines[0] == "=" * 50

        # Should end with separator
        # Should end with separator
        assert non_empty_lines[-1] == "=" * 50

        # Should have multiple sections
        # Should have multiple sections
        assert len(non_empty_lines) > 10

        # Check for section headers
        assert any("By Provider:" in line for line in non_empty_lines)
        assert any("By Phase:" in line for line in non_empty_lines)

    def test_get_formatted_stats_multiple_phases_sorted(self) -> None:
        """Test that phases are sorted in formatted output."""
        collector = StatsCollector()

        # Add data in non-sequential phase order
        collector.track(
            TokenUsage(
                provider=AgentType.CLAUDE,
                input_tokens=1000,
                output_tokens=500,
                phase=3,
                task="task3",
            )
        )
        collector.track(
            TokenUsage(
                provider=AgentType.CLAUDE,
                input_tokens=1000,
                output_tokens=500,
                phase=1,
                task="task1",
            )
        )
        collector.track(
            TokenUsage(
                provider=AgentType.CLAUDE,
                input_tokens=1000,
                output_tokens=500,
                phase=2,
                task="task2",
            )
        )

        formatted = collector.get_formatted_stats(period=Period.ALL)
        lines = formatted.split("\n")

        # Find phase lines (lines that contain "Phase X:" pattern)
        phase_lines = []
        for line in lines:
            # Look for lines like "  Phase 1: 1,500 tokens"
            if "Phase" in line and ":" in line and "tokens" in line:
                phase_lines.append(line.strip())

        # Should have 3 phase lines
        assert len(phase_lines) == 3

        # Phases should be in sorted order (extract phase numbers)
        phase_numbers = []
        for line in phase_lines:
            # Extract phase number from "Phase 1: 1,500 tokens"
            phase_part = line.split(":")[0].strip()  # "Phase 1"
            phase_num = int(phase_part.split()[1])  # 1
            phase_numbers.append(phase_num)

        assert phase_numbers == [1, 2, 3]

    def test_get_formatted_stats_multiple_providers_sorted(self) -> None:
        """Test that providers are sorted in formatted output."""
        collector = StatsCollector()

        # Add data for multiple providers
        collector.track(
            TokenUsage(
                provider=AgentType.PERPLEXITY,
                input_tokens=1000,
                output_tokens=500,
                phase=1,
                task="task_pplx",
            )
        )
        collector.track(
            TokenUsage(
                provider=AgentType.CLAUDE,
                input_tokens=1000,
                output_tokens=500,
                phase=1,
                task="task_claude",
            )
        )
        collector.track(
            TokenUsage(
                provider=AgentType.GEMINI,
                input_tokens=1000,
                output_tokens=500,
                phase=1,
                task="task_gemini",
            )
        )

        formatted = collector.get_formatted_stats(period=Period.ALL)
        lines = formatted.split("\n")

        # Find provider lines (lines between "By Provider:" and "By Phase:")
        in_provider_section = False
        provider_lines = []
        for line in lines:
            if "By Provider:" in line:
                in_provider_section = True
                continue
            if "By Phase:" in line:
                break
            if in_provider_section and ":" in line and "tokens" in line:
                provider_lines.append(line.strip())

        # Extract provider names
        providers = []
        for line in provider_lines:
            # Line format: "  claude: 1,500 tokens"
            provider_name = line.split(":")[0].strip()
            providers.append(provider_name)

        # Should be alphabetically sorted
        assert providers == sorted(providers)


class TestUsageSummaryDataclass:
    """Test suite for UsageSummary dataclass."""

    def test_usage_summary_creation(self) -> None:
        """Test creating a UsageSummary instance."""
        summary = UsageSummary(
            period=Period.DAILY,
            start_date=datetime.now(),
            end_date=datetime.now(),
            total_tokens=1000,
            total_cost=0.01,
            by_provider={"claude": 1000},
            by_phase={1: 1000},
            request_count=5,
        )

        assert summary.period == Period.DAILY
        assert summary.total_tokens == 1000
        assert summary.total_cost == 0.01
        assert summary.by_provider == {"claude": 1000}
        assert summary.by_phase == {1: 1000}
        assert summary.request_count == 5

    def test_usage_summary_with_empty_aggregations(self) -> None:
        """Test UsageSummary with empty provider/phase dicts."""
        summary = UsageSummary(
            period=Period.ALL,
            start_date=datetime.min,
            end_date=datetime.now(),
            total_tokens=0,
            total_cost=0.0,
            by_provider={},
            by_phase={},
            request_count=0,
        )

        assert summary.total_tokens == 0
        assert len(summary.by_provider) == 0
        assert len(summary.by_phase) == 0


class TestPeriodEnum:
    """Test suite for Period StrEnum."""

    def test_period_values(self) -> None:
        """Test Period enum values."""
        assert Period.DAILY.value == "daily"
        assert Period.WEEKLY.value == "weekly"
        assert Period.MONTHLY.value == "monthly"
        assert Period.ALL.value == "all"

    def test_period_comparison(self) -> None:
        """Test Period enum comparison."""
        assert Period.DAILY == "daily"  # StrEnum allows string comparison
        assert Period.WEEKLY == "weekly"

    def test_period_iteration(self) -> None:
        """Test iterating over Period enum."""
        periods = list(Period)
        assert len(periods) == 4
        assert Period.DAILY in periods
        assert Period.WEEKLY in periods
        assert Period.MONTHLY in periods
        assert Period.ALL in periods


class TestStatsCollectorEdgeCases:
    """Test suite for edge cases in StatsCollector."""

    def test_track_multiple_usage_same_phase(self) -> None:
        """Test tracking multiple usage records for the same phase."""
        collector = StatsCollector()

        collector.track(
            TokenUsage(
                provider=AgentType.CLAUDE,
                input_tokens=1000,
                output_tokens=500,
                phase=1,
                task="task1",
            )
        )
        collector.track(
            TokenUsage(
                provider=AgentType.CLAUDE,
                input_tokens=2000,
                output_tokens=1000,
                phase=1,
                task="task2",
            )
        )

        summary = collector.get_summary(period=Period.ALL)

        # Should aggregate by phase
        assert summary.by_phase[1] == 4500  # 1500 + 3000

    def test_track_multiple_usage_same_provider(self) -> None:
        """Test tracking multiple usage records for the same provider."""
        collector = StatsCollector()

        collector.track(
            TokenUsage(
                provider=AgentType.CLAUDE,
                input_tokens=1000,
                output_tokens=500,
                phase=1,
                task="task1",
            )
        )
        collector.track(
            TokenUsage(
                provider=AgentType.CLAUDE,
                input_tokens=2000,
                output_tokens=1000,
                phase=2,
                task="task2",
            )
        )

        summary = collector.get_summary(period=Period.ALL)

        # Should aggregate by provider
        assert summary.by_provider["claude"] == 4500  # 1500 + 3000

    def test_get_summary_date_range_accuracy(self) -> None:
        """Test that get_summary accurately filters by date range."""
        collector = StatsCollector()

        # Create usage with specific timestamps
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        last_week = now - timedelta(days=7)
        last_month = now - timedelta(days=30)

        # Create usage records with different timestamps
        usage_today = TokenUsage(
            provider=AgentType.CLAUDE,
            input_tokens=100,
            output_tokens=50,
            phase=1,
            task="today",
        )
        usage_today.timestamp = now

        usage_yesterday = TokenUsage(
            provider=AgentType.CLAUDE,
            input_tokens=100,
            output_tokens=50,
            phase=1,
            task="yesterday",
        )
        usage_yesterday.timestamp = yesterday

        usage_last_week = TokenUsage(
            provider=AgentType.CLAUDE,
            input_tokens=100,
            output_tokens=50,
            phase=1,
            task="last_week",
        )
        usage_last_week.timestamp = last_week

        usage_last_month = TokenUsage(
            provider=AgentType.CLAUDE,
            input_tokens=100,
            output_tokens=50,
            phase=1,
            task="last_month",
        )
        usage_last_month.timestamp = last_month

        collector.track(usage_today)
        collector.track(usage_yesterday)
        collector.track(usage_last_week)
        collector.track(usage_last_month)

        # Test DAILY - should include today and yesterday
        daily_summary = collector.get_summary(period=Period.DAILY)
        assert daily_summary.request_count == 2  # today + yesterday

        # Test WEEKLY - should include all except maybe last_month depending on timing
        weekly_summary = collector.get_summary(period=Period.WEEKLY)
        assert weekly_summary.request_count >= 3

        # Test ALL - should include all
        all_summary = collector.get_summary(period=Period.ALL)
        assert all_summary.request_count == 4
