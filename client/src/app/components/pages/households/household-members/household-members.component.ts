import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { forkJoin } from 'rxjs';
import { GenericDialogComponent } from '../../../shared/generic-dialog/generic-dialog.component';
import { HouseholdMemberBase as HouseHoldMember } from '../../../../models/HouseholdMemberBase';
import { UserBase as User } from '../../../../models/UserBase';
import { HouseholdBase as Household } from '../../../../models/HouseholdBase';
import { GenericTableComponent, TableColumn } from '../../../shared/generic-table/generic-table.component';
import { ApiResponse } from '../../../../models/apiResponse';
import { FormFactoryService } from '../../../../factories/forms/form-factory.service';
import { FormFieldConfig } from '../../../shared/generic-form/form-config';
import { ToastService } from '../../../../services/toast.service';
import { environment } from '../../../../../environments/environment';
import { HouseholdMemberService } from '../../../../services/household-member.service';
import { UserService } from '../../../../services/user.service';
import { HouseholdService } from '../../../../services/household.service';

@Component({
  selector: 'app-householdmembers',
  imports: [GenericTableComponent],
  templateUrl: './household-members.component.html',
  styleUrl: './household-members.component.css',
})
export class HouseholdmembersComponent implements OnInit {
  houseHoldsMembers: HouseHoldMember[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  isFormValid = false;
  columns: TableColumn<HouseHoldMember>[] = [];
  householdsMap: Record<number, string> = {};
  usersMap: Record<number, string> = {};
  constructor(
    private householdmemberService: HouseholdMemberService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService,
    private householdService: HouseholdService,
    private userService: UserService
  ) {}
  ngOnInit(): void {
    this.columns =this.formFactory.getTableColumns<HouseHoldMember>(
                                                                    'houseHoldMember',
                                                                    {user_id:  (value: number) => this.usersMap[value] ?? value, household_id: (value: number) => this.householdsMap[value] ?? value });
    this.loadHouseHoldMembers();
  }
  loadHouseHoldMembers() {
    this.isLoading = true;
    this.householdmemberService.getAll().subscribe({
      next: (data: ApiResponse<HouseHoldMember[]>) => {
        this.houseHoldsMembers = data.response;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'Error loading HouseHold Members';
        this.isLoading = false;
      },
    });

    this.householdService.getAll().subscribe({
      next: (res: ApiResponse<Household[]>) => {
        const householdField = this.formFields.find(f => f.key === 'household_id');
        if (householdField) {
          this.householdsMap = Object.fromEntries(res.response.map(h=>[h.id,h.name]));
        }
      }
    });
    this.userService.getUsers().subscribe({
      next: (res: ApiResponse<User[]>) => {
        const userField = this.formFields.find(f => f.key === 'user_id');
        if (userField) {
          this.usersMap = Object.fromEntries(res.response.map((u: User)=>[u.id, (`${u.name} ${u.surname1} ${u.surname2}`)]))
        }
      }
    });
  }
  editHouseHoldMember(householdmember: HouseHoldMember) {
    this.openDialog(householdmember);

  }
  addHouseHoldMember() {
    this.openDialog();
  }

  openDialog(data?: HouseHoldMember): void {
  // 1. Cargar TODO en paralelo antes de abrir el diálogo
  forkJoin({
    households: this.householdService.getAll(),
    users: this.userService.getUsers()
  }).subscribe({
    next: (responses) => {
      const baseConfig = this.formFactory.getFormConfig('houseHoldMember');

      // 2. Enriquecer directamente los campos con las opciones
      const enrichedConfig = baseConfig.map((field: FormFieldConfig) => {
        if (field.key === 'household_id') {
          return {
            ...field,
            options: responses.households.response.map((h: Household) => ({
              value: h.id,
              label: h.name
            }))
          };
        }

        if (field.key === 'user_id') {
          return {
            ...field,
            options: responses.users.response.map((u: User) => ({
              value: u.id,
              label: `${u.name} ${u.surname1} ${u.surname2}`
            }))
          };
        }

        return field;
      });

      // 3. Abrir el diálogo SOLO cuando los datos estén listos
      const dialogRef = this.dialog.open(GenericDialogComponent, {
        data: {
          title: data ? 'Edit Household Member' : 'New Household Member',
          fields: enrichedConfig,
          initialData: data || {}
        }
      });

      dialogRef.afterClosed().subscribe(result => {
        if (result) {
          result.id ? this.updateHouseHoldMember(result) : this.createHouseHoldMember(result);
        }
      });
    },
    error: (error) => {
      console.error('Error loading data:', error);
    }
  });
}

  updateHouseHoldMember(householdMember: HouseHoldMember): void {
    this.householdmemberService.update(householdMember.id, householdMember).subscribe({
    next: (response: ApiResponse<HouseHoldMember>) => {
      const updated = response.response;
      const index = this.houseHoldsMembers.findIndex(h => h.id === updated.id);
      if (index !== -1) {
        this.houseHoldsMembers[index] = updated;
        this.houseHoldsMembers = [...this.houseHoldsMembers];
      }
      this.toastService.showToast(response, environment.toastType.Success, {});
      this.cdr.detectChanges();
    },
    error: (err) => {
      this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
    }
  });
  }
  createHouseHoldMember(householdMember: HouseHoldMember): void {
    this.householdmemberService.create(householdMember).subscribe({
    next: (response: ApiResponse<HouseHoldMember>) => {
      this.houseHoldsMembers.push(response.response);
      this.houseHoldsMembers = [...this.houseHoldsMembers];
      this.toastService.showToast(response, environment.toastType.Success, {});
      this.cdr.detectChanges();
    },
    error: (err) => {
      this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
    }
  });
  }
}
