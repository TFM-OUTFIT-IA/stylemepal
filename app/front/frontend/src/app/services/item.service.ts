import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ItemService {
  private apiUrl = 'http://localhost:8000/api/items';

  constructor(private http: HttpClient) {}

  getItems(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl);
  }

  // Subir archivo con FormData
  createItem(image: File, nombre: string): Observable<any> {
    const formData = new FormData();
    formData.append('image', image);
    formData.append('nombre', nombre);
    return this.http.post<any>(this.apiUrl, formData);
  }

  updateItem(id: number, data: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/${id}`, data);
  }

  deleteItem(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/${id}`);
  }

  cleanAllItems(): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/bulk/clean-all`, {});
  }

  
  confirmOutfit(ids: number[]): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/bulk/dirty`, { ids });
  }
}