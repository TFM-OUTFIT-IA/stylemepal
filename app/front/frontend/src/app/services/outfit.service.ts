import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class OutfitService {
  private apiUrl = '/api/v1/outfits';

  constructor(private http: HttpClient) {}

  saveOutfit(payload: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, payload);
  }

  getOutfits(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl);
  }

  deleteOutfit(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/${id}`);
  }
}