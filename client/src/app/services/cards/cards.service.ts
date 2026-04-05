import { BaseCrudService } from '@core_services/base-crud.service';
import { HttpClient } from '@angular/common/http';
import { CardBase as Card } from '@cards_models/CardBase';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/internal/Observable';
import { ApiResponse } from '@app/models/core/APIResponse';

@Injectable({
  providedIn: 'root',
})
export class CardService extends BaseCrudService<Card> {
  constructor(protected override http: HttpClient) {
    super(http, 'cards');
  }
/**
   * Alias for getAll() - Get all cards
   */
  getCards(): Observable<ApiResponse<Card[]>> {
    return this.getAll();
  }

  /**
   * Alias for create() - Create a new card
   */
  createCard(card: Card): Observable<ApiResponse<Card>> {
    return this.create(card);
  }

  /**
   * Alias for update() - Update an existing card
   */
  updateCard(id: number, card: Card): Observable<ApiResponse<Card>> {
    return this.update(id, card);
  }
}
