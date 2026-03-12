import { NgModule } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatBadgeModule } from '@angular/material/badge';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatOption } from '@angular/material/core';
import { MatSelectModule } from '@angular/material/select';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatDividerModule } from '@angular/material/divider';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatGridList, MatGridTile } from '@angular/material/grid-list';
import { MatDialogModule } from '@angular/material/dialog';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltip } from '@angular/material/tooltip';
import { MatSidenav } from '@angular/material/sidenav';
import { MatListItem } from '@angular/material/list';
import { MAT_DATE_FORMATS, MAT_DATE_LOCALE } from '@angular/material/core';
import { MatListItemMeta } from '@angular/material/list';
import { MatListItemTitle } from '@angular/material/list';

import { environment } from '@env/environment';


@NgModule({
  imports: [
    MatButtonModule,
    MatIconModule,
    MatMenuModule,
    MatToolbarModule,
    MatSidenavModule,
    MatListModule,
    MatDividerModule,
    MatCardModule,
    MatFormFieldModule,
    MatGridList,
    MatGridTile,
    MatDialogModule,
    MatInputModule,
    MatCheckboxModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatExpansionModule,
    MatBadgeModule,
    MatOption,
    MatSelectModule,
    MatProgressSpinnerModule,
    MatTooltip,
    MatSidenav,
    MatListItem,
    MatListItemMeta,
    MatListItemTitle
  ],
  exports: [
    MatButtonModule,
    MatIconModule,
    MatMenuModule,
    MatToolbarModule,
    MatSidenavModule,
    MatListModule,
    MatDividerModule,
    MatCardModule,
    MatFormFieldModule,
    MatGridList,
    MatGridTile,
    MatDialogModule,
    MatInputModule,
    MatCheckboxModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatExpansionModule,
    MatBadgeModule,
    MatOption,
    MatSelectModule,
    MatProgressSpinnerModule,
    MatTooltip,
    MatSidenav,
    MatListItem,
    MatListItemMeta,
    MatListItemTitle
  ],
  providers: [
    { provide: MAT_DATE_LOCALE, useValue: environment.locations.defaultLocation }, // 'en-GB' uses DD-MM-YYYY by default
    { provide: MAT_DATE_FORMATS, useValue: environment.date_formats }
  ]
})

export class MaterialModule {}
