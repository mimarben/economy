import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { GenericTableComponent, TableColumn } from '@shared/generic-table/generic-table.component';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { FormFactoryService } from '@app/core/factories/form-factory.service';
import { MetaService } from '@core_services/meta.service';
import { SourceRuleService, SourceRule } from '@app/services/rules/source-rule.service';
import { SourceService } from '@finance_services/source.service';

@Component({
  selector: 'app-source-rules',
  standalone: true,
  imports: [GenericTableComponent],
  templateUrl: './source-rules.component.html',
  styleUrls: ['./source-rules.component.scss'],
})
export class SourceRulesComponent implements OnInit {
  rules: SourceRule[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  columns: TableColumn<SourceRule>[] = [];

  constructor(
    private sourceRuleService: SourceRuleService,
    private sourceService: SourceService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private formFactory: FormFactoryService,
    private metaService: MetaService,
  ) {}

  ngOnInit(): void {
    this.sourceService.getAll().subscribe({
      next: (resp) => {
        const sourceOptions = (resp?.response || [])
          .filter((s) => s.id !== undefined && s.id !== null)
          .map((s) => ({ value: s.id as number, label: s.name }));

        this.metaService.getMeta('source_rule').subscribe((meta) => {
          const enriched = this.formFactory.enrichMetadataFields(meta.fields, {
            source_id: sourceOptions,
          });
          this.formFields = [{ key: 'id', label: 'Id', type: 'number' }, ...enriched];
          this.columns = [
            { key: 'id', label: 'Id', sortable: true },
            ...this.formFactory.getTableColumnsFromMetadata(enriched),
          ];
          this.loadRules();
        });
      },
      error: (err: unknown) => console.error('Error loading sources:', err),
    });
  }

  loadRules(): void {
    this.isLoading = true;
    this.sourceRuleService.getAllRules().subscribe({
      next: (rules) => {
        this.rules = rules;
        this.isLoading = false;
      },
      error: (err: unknown) => {
        this.errorMessage = 'Failed to load rules.';
        console.error('Error loading rules:', err);
        this.isLoading = false;
      },
    });
  }

  editRule(rule: SourceRule): void {
    this.openDialog(rule);
  }

  addRule(): void {
    this.openDialog();
  }

  deleteRule(rule: SourceRule): void {
    if (!rule.id || !confirm(`Delete rule "${rule.name}"?`)) return;
    this.sourceRuleService.deleteRule(rule.id).subscribe({
      next: () => {
        this.rules = this.rules.filter((r) => r.id !== rule.id);
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.errorMessage = 'Failed to delete rule.';
        console.error('Error deleting rule:', err);
      },
    });
  }

  private openDialog(data?: SourceRule): void {
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit Source Rule' : 'New Source Rule',
        fields: this.formFields,
        initialData: data || {},
      },
    });
    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        result.id ? this.updateRule(result) : this.createRule(result);
      }
    });
  }

  private createRule(rule: SourceRule): void {
    this.sourceRuleService.createRule(rule).subscribe({
      next: (created) => {
        this.rules = [...this.rules, created];
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.errorMessage = 'Failed to create rule.';
        console.error('Error creating rule:', err);
      },
    });
  }

  private updateRule(rule: SourceRule): void {
    this.sourceRuleService.updateRule(rule.id!, rule).subscribe({
      next: (updated) => {
        const index = this.rules.findIndex((r) => r.id === updated.id);
        if (index !== -1) {
          this.rules[index] = updated;
          this.rules = [...this.rules];
        }
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.errorMessage = 'Failed to update rule.';
        console.error('Error updating rule:', err);
      },
    });
  }

  applyFilter(event: Event): void {
    this.filterValue = (event.target as HTMLInputElement).value.trim().toLowerCase();
  }
}
