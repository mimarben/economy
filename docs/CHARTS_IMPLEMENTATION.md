# Dashboard Charts Implementation

This document describes the complete implementation of the charts and summary functionality for the Economy application.

## Backend Architecture

### Endpoint: `/summary`

#### Query Parameters:
- `period`: 'week' | 'month' | 'year' | 'custom' (default: 'month')
- `start_date`: YYYY-MM-DD format (required for 'custom' period)
- `end_date`: YYYY-MM-DD format (required for 'custom' period)

#### Response Format:
```json
{
  "data": {
    "period_start": "2026-01-01",
    "period_end": "2026-03-26",
    "totals_by_category": [
      {
        "category_id": 1,
        "category_name": "Groceries",
        "type": "expense",
        "total": 150.50
      }
    ],
    "totals_over_time": [
      {
        "date": "2026-01-01",
        "expense": 50.0,
        "income": 2000.0,
        "investment": 100.0,
        "net": 1850.0
      }
    ],
    "income_vs_expense": {
      "total_income": 10000.0,
      "total_expense": 5000.0,
      "net": 5000.0,
      "count_transactions": 150
    }
  }
}
```

### Backend Files

#### Schemas (`api/schemas/summaries/`)
- `summary_schema.py`: Pydantic models for API responses
  - `TotalByCategory`: Category-level aggregation
  - `TotalOverTime`: Daily aggregation by transaction type
  - `IncomeVsExpense`: Summary statistics
  - `SummaryResponse`: Complete response object

#### Repository (`api/repositories/summaries/`)
- `summary_repository.py`: Data access layer
  - `get_totals_by_category()`: Aggregates by category and type
  - `get_totals_over_time()`: Aggregates daily data
  - `get_income_vs_expense()`: Summary statistics

#### Service (`api/services/summaries/`)
- `summary_service.py`: Business logic
  - `get_summary()`: Custom date range
  - `get_week_summary()`: Current week (Monday-Sunday)
  - `get_month_summary()`: Current month
  - `get_year_summary()`: Current year

#### Router (`api/routers/summaries/`)
- `summary_router.py`: API endpoints
  - `GET /summary`: Custom range with dates
  - `GET /summary/week`: Week summary
  - `GET /summary/month`: Month summary
  - `GET /summary/year`: Year summary

### Usage Examples

**Current Month:**
```bash
curl http://localhost:5000/api/summary/month
```

**Custom Date Range:**
```bash
curl "http://localhost:5000/api/summary?start_date=2026-01-01&end_date=2026-03-31"
```

**This Week:**
```bash
curl http://localhost:5000/api/summary/week
```

---

## Frontend Architecture

### Module: Charts (`client/src/app/modules/charts/`)

#### Components

1. **ChartsContainerComponent** (`charts-container/`)
   - Main container managing filters and chart layout
   - Handles period selection (week/month/year/custom)
   - Routes data to child chart components
   - Responsive 2x2 grid layout

2. **ExpenseChartComponent** (`expense-chart/`)
   - Doughnut chart showing expenses by category
   - Dynamic color palette
   - Category-based breakdown

3. **IncomeChartComponent** (`income-chart/`)
   - Doughnut chart showing income by category
   - Similar to expense chart but with distinct colors
   - Handles empty states

4. **InvestmentChartComponent** (`investment-chart/`)
   - Pie chart for investment allocation
   - Shows investment categories
   - Graceful empty state handling

5. **ComparisonChartComponent** (`comparison-chart/`)
   - Line chart with multiple datasets
   - Shows Income, Expense, and Net over time
   - Daily granularity with formatted date labels

### Service: SummaryService (`client/src/app/services/`)

```typescript
// Get custom range
getSummary(startDate: string, endDate: string): Observable<{data: SummaryResponse}>

// Get predefined periods
getWeekSummary(): Observable<{data: SummaryResponse}>
getMonthSummary(): Observable<{data: SummaryResponse}>
getYearSummary(): Observable<{data: SummaryResponse}>
```

### Module Imports

```typescript
ChartsModule exports:
- ChartsContainerComponent (main public API)

Imports internally:
- CommonModule
- MatCardModule
- MatSelectModule
- MatDatepickerModule
- MatNativeDateModule
- MatButtonModule
- MatGridListModule
- NgChartsModule (ng2-charts)
- ReactiveFormsModule
```

### Styling

- Border-radius: 16px for Material Design consistency
- 8px-based spacing scale
- Responsive grid: 2 columns on desktop, adapts on tablets
- Dark theme support ready
- Chart containers maintain aspect ratio with flexible heights

---

## Integration Steps

### 1. Backend Registration

The summary router is automatically registered in `api/routers/__init__.py`:

```python
from .summaries.summary_router import router as summary_router

blueprints = [
    # ... existing routers ...
    summary_router
]
```

### 2. Frontend Integration

Import and use in your app module or routing:

```typescript
import { ChartsModule } from './modules/charts/charts.module';

@NgModule({
  imports: [
    // ... other imports ...
    ChartsModule,
  ]
})
export class AppModule { }
```

In component template:
```html
<app-charts-container></app-charts-container>
```

### 3. Dependencies

**Backend Python:**
```
SQLAlchemy (already installed)
Flask (already installed)
Pydantic (already installed)
```

**Frontend npm:**
```
ng2-charts (must install)
chart.js (must install)

npm install ng2-charts chart.js
```

---

## Data Flow

```
Frontend (ChartsContainerComponent)
    ↓
    [Period Selection: week/month/year/custom]
    ↓
SummaryService.getXxxSummary()
    ↓
HTTP GET /api/summary
    ↓
Backend (SummaryRouter)
    ↓
SummaryService.get_summary()
    ↓
SummaryRepository
    ↓
Database Queries (Expenses, Incomes, Investments)
    ↓
Aggregated Response JSON
    ↓
Frontend Chart Components
    ↓
Visual Representation
```

---

## Filter Behavior

### Week Filter
- Monday - Sunday of current week
- Automatically calculated

### Month Filter
- 1st - Last day of current month
- Handles February and leap years

### Year Filter
- January 1 - December 31 of current year

### Custom Range
- Datepicker UI for start and end dates
- Manual validation: start_date ≤ end_date
- Formats dates to YYYY-MM-DD for API

---

## Performance Considerations

1. **Database Queries**: Indexed by `(type, date)` for fast aggregations
2. **Frontend Rendering**: OnPush change detection (optional enhancement)
3. **Chart Updates**: Immutable updates trigger change detection
4. **Data Caching**: Consider RxJS `shareReplay()` for repeated requests

---

## Known Limitations

1. **Investment handling**: Empty investment data shows "No data" placeholder
2. **Large date ranges**: Consider pagination for year+ summaries
3. **Timezone awareness**: Uses device timezone for date calculations

---

## Future Enhancements

- [ ] Export summary as PDF/CSV
- [ ] Comparison between periods (YoY, MoM)
- [ ] Budget vs actual visualization
- [ ] Forecast trends
- [ ] Mobile-optimized charts
- [ ] Dark mode theme
- [ ] Category drill-down details
