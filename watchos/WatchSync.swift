import Foundation

class WatchSync: ObservableObject {
    let baseURL: String
    let userId: String
    @Published var version: Int = 0
    @Published var memories: [[String: String]] = []

    init(baseURL: String, userId: String) {
        self.baseURL = baseURL
        self.userId = userId
    }

    func sync(since: Int, completion: @escaping ([[String:String]]) -> Void) {
        guard let url = URL(string: "\(baseURL)/v1/watch/sync?user_id=\(userId)&since_version=\(since)") else { return }
        URLSession.shared.dataTask(with: url) { data, _, _ in
            guard let data = data,
                  let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let mems = json["memories"] as? [[String:String]] else { return }
            DispatchQueue.main.async {
                self.memories = mems
                self.version = json["version"] as? Int ?? since
                completion(mems)
            }
        }.resume()
    }

    func push(title: String, body: String) {
        guard let url = URL(string: "\(baseURL)/v1/watch/push") else { return }
        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = try? JSONSerialization.data(withJSONObject: ["user_id": userId, "title": title, "body": body])
        URLSession.shared.dataTask(with: req).resume()
    }
}
